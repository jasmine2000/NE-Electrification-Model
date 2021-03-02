import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import os.path
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVC, LinearSVC
from sklearn import svm
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.model_selection import train_test_split
from sklearn import metrics

# load adjusted population data 
# (only considers % of people using natural gas as primary source of fuel)
population_data = pd.read_csv('./population_adjusted/CT.csv')

# grab list of census tracts
census_tracts = population_data['geo_id']

# 20 farenheit = -6.66 celsius
# 40 farenheit = 4.44 celsius
# 72 farenheit = 22.22 celsius

# define cutoffs and initialize empty dictionary
cutoffs = {-6.66: 'group_one', 4.44: 'group_two', 22.22: 'group_three'}
monthly_hdh = {}
unheated_hours = {}
for i in range(1, 13):
    monthly_hdh[i] = {'group_one': 0, 'group_two': 0, 'group_three': 0}
    unheated_hours[i] = 0

size = census_tracts.size
count = 1
for geo_id in census_tracts:

    # while running this will inform user of progress
    progress = str(count) + '/' + str(size)
    print(progress)
    count += 1

    # load hourly temperature data for given census tract
    folder = Path('./temp_data/')
    folder.mkdir(parents=True, exist_ok=True)
    completeName = os.path.join(folder, str(geo_id)+".csv")
    hourly_data = pd.read_csv(completeName)

    # iterate over hourly data for year 2019
    for index, row in hourly_data.iterrows():
        year = int(row['local_time'][:4])
        month = int(row['local_time'][5:7])
        if year != 2019: # hourly data includes 12/31/2018- throw this out
            continue
        
        temp = float(row['temperature'])

        # define cutoff group that temperature falls in (see line 19-24)
        group = None
        for cutoff in cutoffs:
            if temp < cutoff:
                group = cutoffs[cutoff]
                break

        # if it is not less than the top cutoff (72 deg farenheit),
        # no fuel is used for heating
        if group is None:
            unheated_hours[month] += 1

        else: # calcuate heating degree hours and add to group
            hdh = 22.22 - temp
            monthly_hdh[month][group] += hdh
        

# initialize empty dataframe to put data in
d = {'group_one': [], 'group_two': [], 'group_three': [], 'y': []}
df = pd.DataFrame(data=d)

# data from eia.gov for monthly residential gas consumption
y_vals = [9800, 8189, 7201, 3792, 2278, 1338, 1025, 933, 1066, 1974, 6140, 8492]

# take aggregated data and put into dataframe along with y vals
for month in monthly_hdh:
    entry = monthly_hdh[month]
    entry['y'] = y_vals[month - 1]
    df = df.append(entry, ignore_index=True)

# save copy of data
df.to_csv('data.csv', index=False)

# standardize data
cols = list(df.columns)
for col in cols:
    col_zscore = col + '_standardized'
    df[col_zscore] = (df[col] - df[col].mean())/df[col].std(ddof=0)

# drop unstandardized clumns (reference data.csv for these)
df = df.drop(['group_one', 'group_two', 'group_three', 'y'], axis=1)
df.to_csv('standardized_data.csv', index=False)

# run regression
X = df.drop(['y_standardized'], axis=1)
y = df['y_standardized']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state=42) # test size needs to be checked

reg = LinearRegression()
reg.fit(X_train, y_train)
predictions = reg.predict(X_test)

# get info on regression performance
mae = metrics.mean_absolute_error(y_test, predictions)
mse = metrics.mean_squared_error(y_test, predictions)
r_squared = str(round(reg.score(X, y), 3))
coefficients = reg.coef_

# write results into file
# results.txt is regression on unsplit data
results = open("results_2.txt","w+")
results.write('r_squared: ' + r_squared + '\n')
results.write('group_one: ' + str(coefficients[0]) + '\n')
results.write('group_two: ' + str(coefficients[1]) + '\n')
results.write('group_three: ' + str(coefficients[2]) + '\n\n')
results.write('mean absolute error: ' + str(mae) + '\n')
results.write('mean squared error: ' + str(mse) + '\n')
