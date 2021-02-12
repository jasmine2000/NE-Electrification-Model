import pandas as pd

data = pd.read_csv('population_data.csv')

ne = ['CT', 'ME', 'MA', 'NH', 'NJ', 'NY', 'PA', 'RI', 'VT']
ne_data= data[data.STUSAB.isin(ne)]

ne_data['GISJOIN'] = ne_data['GISJOIN'].str.slice(2, 14)

print(ne_data.head())