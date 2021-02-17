import pandas as pd

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

# new dataset
d = {'geo_id': [], 'new_population': []}
df = pd.DataFrame(data=d)

for index, row in ne_data.iterrows():
    geo_id = row['GEOID'][7:]
    print(geo_id)
    if str(geo_id)[0] == '0':
        geo_id = geo_id[1:]

    pop = row['ALUBE001']
    
    percent = gas.loc[gas['GEOID'] == geo_id, 'B25040_calc_pctUGE'].iloc[0]

    actual_pop = pop * float(percent)/100

    entry = {'geo_id': geo_id, 'new_population': actual_pop}
    df = df.append(entry, ignore_index=True)

    # entry = {'geo_id': geo_id, 'new_population': actual_pop}
    # df.append(entry, ignore_index=True)

    print(df.head())

    break