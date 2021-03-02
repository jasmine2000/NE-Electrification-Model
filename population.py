import pandas as pd
from pathlib import Path
import os.path

# filter population data
population = pd.read_csv('population_data.csv')

ne = ['CT', 'ME', 'MA', 'NH', 'NJ', 'NY', 'PA', 'RI', 'VT']
ne_data= population[population.STUSAB.isin(ne)]

# filter gas data and cast all to string for comparison purposes
gas = pd.read_csv('gas_data.csv')
gas = gas.applymap(str)

# drop everything except necessary columns
# estmated % and margin of error on this % (don't end up using margin)
keep = ['X', 'Y', 'OBJECTID', 'GEOID', 'NAME', 'State', 'County', 'B25040_calc_pctUGE', 'B25040_calc_pctUGM']
for (columnName, columnData) in gas.iteritems(): 
    if columnName not in keep:
        gas = gas.drop(columnName, axis=1)

for state in ne:
    # filter data to just one state
    state_data= ne_data[ne_data.STUSAB.isin([state])]

    # new dataset
    d = {'geo_id': [], 'new_population': []}
    df = pd.DataFrame(data=d)

    for index, row in state_data.iterrows():
        # geo_ids in this file are in format "14000US01001020100", cut out "14000US"
        geo_id = row['GEOID'][7:] 
        
        # gas data was originally int form 
        # geo ids that began with 0 dropped the 0
        if str(geo_id)[0] == '0': 
            geo_id = geo_id[1:]

        pop = row['ALUBE001']
        
        # perform calcuations and note tracts with missing into (there were 2)
        try:
            percent = gas.loc[gas['GEOID'] == geo_id, 'B25040_calc_pctUGE'].iloc[0]
        except IndexError:
            percent = 100
            print(geo_id)

        actual_pop = round(pop * float(percent)/100, 2)

        entry = {'geo_id': geo_id, 'new_population': actual_pop}
        df = df.append(entry, ignore_index=True)

    # once an entire state is finished save the file to directory
    save_path = Path('./population_adjusted/')
    save_path.mkdir(parents=True, exist_ok=True)
    filename = str(state)+".csv"
    completeName = os.path.join(save_path, filename)         

    df.to_csv(completeName, index=False)

    break # currently only have temperature data for CT


