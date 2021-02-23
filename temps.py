import pandas as pd
from pathlib import Path
import requests
import json
import os.path
import time

data = pd.read_csv("coordinates.csv")
ne = ['CT', 'ME', 'MA', 'NH', 'NJ', 'NY', 'PA', 'RI', 'VT']
ne_data= data[data.USPS.isin(ne)]

token = '039ea943f8cfb043738a4de2be5b5245d1e8dbef'
api_base = 'https://www.renewables.ninja/api/'

s = requests.session()
# Send token header with each request
s.headers = {'Authorization': 'Token ' + token}

url = api_base + 'data/weather'

count = 0

for index, row in ne_data.iterrows():
    count += 1
    print(count)

    geo_id = row['GEOID']
    p = './temp_data/' + str(geo_id) + '.csv'
    if os.path.exists(p):
        continue
    else:
        lat = row['INTPTLAT']
        lon = row['INTPTLONG']

        args = {
            'lat': lat,
            'lon': lon,
            'date_from': '2019-01-01',
            'date_to': '2019-12-31',
            'dataset': 'merra2',
            'local_time': True,
            'var_t2m': True,
            # 'var_prectotland': True,
            'format': 'json',
            'header': True
        }

        r = s.get(url, params=args)        

        # Parse JSON to get a pandas.DataFrame of data and dict of metadata
        parsed_response = json.loads(r.text)

        data = pd.read_json(json.dumps(parsed_response['data']), orient='index')
        metadata = parsed_response['metadata']

        # save to temp_data folder
        save_path = Path('./temp_data/')
        save_path.mkdir(parents=True, exist_ok=True)
        filename = str(geo_id)+".csv"
        completeName = os.path.join(save_path, filename)

        data.to_csv(completeName, index=False)

        if count % 50 == 0:
            time.sleep(3300)
        
        time.sleep(10)