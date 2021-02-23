import pandas as pd
from pathlib import Path
import os.path

# filter population data
population = pd.read_csv('population_data.csv')

ne = ['CT', 'ME', 'MA', 'NH', 'NJ', 'NY', 'PA', 'RI', 'VT']
ne_data= population[population.STUSAB.isin(ne)]

# filter gas data
gas = pd.read_csv('gas_data.csv')
gas = gas.applymap(str)

keep = ['X', 'Y', 'OBJECTID', 'GEOID', 'NAME', 'State', 'County', 'B25040_calc_pctUGE', 'B25040_calc_pctUGM']
for (columnName, columnData) in gas.iteritems(): 
    if columnName not in keep:
        gas = gas.drop(columnName, axis=1)

for state in ne:
    state_data= ne_data[ne_data.STUSAB.isin([state])]
    # new dataset
    d = {'geo_id': [], 'new_population': []}
    df = pd.DataFrame(data=d)

    for index, row in state_data.iterrows():
        geo_id = row['GEOID'][7:]
        if str(geo_id)[0] == '0':
            geo_id = geo_id[1:]

        pop = row['ALUBE001']
        
        try:
            percent = gas.loc[gas['GEOID'] == geo_id, 'B25040_calc_pctUGE'].iloc[0]
        except IndexError:
            percent = 100
            print(geo_id)

        actual_pop = round(pop * float(percent)/100, 2)

        entry = {'geo_id': geo_id, 'new_population': actual_pop}
        df = df.append(entry, ignore_index=True)

    save_path = Path('./population_adjusted/')
    save_path.mkdir(parents=True, exist_ok=True)
    filename = str(state)+".csv"
    completeName = os.path.join(save_path, filename)         

    df.to_csv(completeName, index=False)

    break


