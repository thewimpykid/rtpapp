import requests
from datetime import datetime
import pytz
import pickle
import numpy as np

def getCurrentPrice(state):
    timezone = pytz.timezone('UTC') 
    time_in_state = datetime.now(timezone)
    current_time_years = time_in_state.strftime("%Y")
    current_time_months = time_in_state.strftime("%m")
    current_time_days = time_in_state.strftime("%d")
    current_time_hours = str(int(time_in_state.strftime("%H")) - 1)
    time = f'{current_time_years}-{current_time_months}-{current_time_days}T{current_time_hours}'
    print(time)
    eia_api = requests.get(f'https://api.eia.gov/v2/electricity/rto/region-data/data/?frequency=hourly&data[0]=value&facets[type][]=D&facets[type][]=DF&facets[respondent][]={state}&start=2022-01-16T00&end={time}&sort[0][column]=period&sort[0][direction]=asc&offset=0&length=5000&api_key=S0WdpfjSTJbuTuahlzvRmS8ZvW2aCoMktJvmL4E4')
    eia_api_json = eia_api.json()
    response = eia_api_json['response']['data']
    # print(eia_api_json)
    run = True
    while run:
        for item in response:
            if item['type-name'] == 'Demand':
                demand = item['value']
                run = False
    print(demand)
    with open('./home/model_pickle', 'rb') as f:
        model = pickle.load(f)
    test = np.array([demand]).reshape((-1, 1))
    price = model.predict(test) 
    return round(price[0], 1)

getCurrentPrice('NY')
