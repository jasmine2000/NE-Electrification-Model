import pandas as pd
from pathlib import Path
import os.path
from sklearn.linear_model import LinearRegression

population_data = pd.read_csv('./population_adjusted/CT.csv')

census_tracts = population_data['geo_id']

# 20 farenheit = -6.66 celsius
# 40 farenheit = 4.44 celsius
# 72 farenheit = 22.22 celsius

cutoffs = {-6.66: 'group_one', 4.44: 'group_two', 22.22: 'group_three'}
monthly_hdh = {}
unheated_hours = {}
for i in range(1, 13):
    monthly_hdh[i] = {'group_one': 0, 'group_two': 0, 'group_three': 0}
    unheated_hours[i] = 0

size = census_tracts.size
count = 1
for geo_id in census_tracts:
    progress = str(count) + '/' + str(size)
    print(progress)
    count += 1
    folder = Path('./temp_data/')
    folder.mkdir(parents=True, exist_ok=True)
    completeName = os.path.join(folder, str(geo_id)+".csv")
    hourly_data = pd.read_csv(completeName)

    for index, row in hourly_data.iterrows():
        year = int(row['local_time'][:4])
        month = int(row['local_time'][5:7])
        if year != 2019:
            continue
        
        temp = float(row['temperature'])

        group = None
        for cutoff in cutoffs:
            if temp < cutoff:
                group = cutoffs[cutoff]
                break

        if group is None:
            unheated_hours[month] += 1
        else:
            hdh = 22.22 - temp
            monthly_hdh[month][group] += hdh
        

d = {'group_one': [], 'group_two': [], 'group_three': [], 'y': []}
df = pd.DataFrame(data=d)

y = [9800, 8189, 7201, 3792, 2278, 1338, 1025, 933, 1066, 1974, 6140, 8492]
adjusted = [(m - min(y))*1000000 for m in y]

for month in monthly_hdh:
    entry = monthly_hdh[month]
    entry['y'] = adjusted[month - 1]
    df = df.append(entry, ignore_index=True)

df.to_csv('final_data.csv', index=False)

X = df.drop(['y'], axis=1)
y = df['y']

reg = LinearRegression().fit(X, y)
r_squared = str(round(reg.score(X, y), 3))
coefficients = reg.coef_

results = open("results.txt","w+")
results.write('r_squared: ' + r_squared + '\n')
results.write('group_one: ' + str(coefficients[0]) + '\n')
results.write('group_two: ' + str(coefficients[1]) + '\n')
results.write('group_three: ' + str(coefficients[2]) + '\n')
