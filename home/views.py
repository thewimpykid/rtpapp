from django.shortcuts import render, redirect
from django.http import HttpResponse
import requests
import matplotlib.pyplot as plt
import numpy as np
from django.template import loader
from datetime import datetime
import plotly.express as px
import pandas as pd
import pytz
import pickle
import numpy as np
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def index(request):
    demand = 0
    if request.method == "POST":
        things = request.POST["states"].split(" ")
        state_eia = things[1]
        state = things[2]
        if state == "NewJersey":
            state = "New Jersey"
    else:
        state_eia = "NY"
        state = "New York"
    
    print('1')
    time = pytz.timezone("utc") 
    
    # initialize var

    # make requests

    # turn requests into json

    # get current price
    print('3')
    timezone = pytz.timezone('UTC') 
    time_in_state = datetime.now(timezone)
    current_time_years = time_in_state.strftime("%Y")
    current_time_months = time_in_state.strftime("%m")
    current_time_days = str(int(time_in_state.strftime("%d")) + 10)
    current_time_hours = int(str(time_in_state.strftime("%H")))
    time = f'{current_time_years}-{current_time_months}-{current_time_days}T{current_time_hours}'
    past_time = f'{current_time_years}-{current_time_months}-{int(int(current_time_days) - 3)}T{current_time_hours}'
    print(current_time_hours)
    if int(current_time_hours) < 10:
            current_time_hours = f'0{current_time_hours}'
            time = f'{current_time_years}-{current_time_months}-{current_time_days}T{current_time_hours}'
            past_time = f'{current_time_years}-{current_time_months}-{int(current_time_days - 3)}T{current_time_hours}'
    # if int(current_time_days) < 10:
    #         current_time_dayss = current_time_days
    #         current_time_days = f'0{current_time_days}'
    #         time = f'{current_time_years}-{current_time_months}-{current_time_days}T{current_time_hours}'
    #         past_time = f'{current_time_years}-{current_time_months}-0{int(int(current_time_dayss) - 3)}T{current_time_hours}'
    eia_api = requests.get(f'https://api.eia.gov/v2/electricity/rto/region-data/data/?frequency=hourly&data[0]=value&facets[type][]=D&facets[type][]=DF&facets[respondent][]={state_eia}&start={past_time}&end={time}&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000&api_key=S0WdpfjSTJbuTuahlzvRmS8ZvW2aCoMktJvmL4E4')
    print(eia_api)
    eia_api_json = eia_api.json()
    response = eia_api_json['response']['data']
    print(eia_api)
    response.reverse()
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
    print(price) 
    
    currentPrice = round(price[0], 1)
    print('5')
    # get current time
    # get fiveminfeed

    # compare results and make a rating


    template = loader.get_template('food/index.html')
    USDPMF = int(round(float(currentPrice) * 2.5, 0))
    USDPMW = int(round(float(currentPrice) * 1.2, 0))
    USDPMC = int(round(float(currentPrice) * 0.90, 0))


  
    context = {
        'USDPM': currentPrice,
        'USDPMF': USDPMF,
        'USDPMC': USDPMC,
        'USDPMW': USDPMW,
        'state': state
    }
    print('6')
 
    return HttpResponse(template.render(context, request))

@csrf_exempt
def past(request):
    demand = 0
    if request.method == "POST":
        things = request.POST["states"].split(" ")
        state_eia = things[1]
        state = things[2]
        if state == "NewJersey":
            state = "New Jersey"
    else:
        state_eia = "NY"
        state = "New York"
    
    timezone = pytz.timezone('UTC') 
    time_in_state = datetime.now(timezone)
    current_time_years = time_in_state.strftime("%Y")
    current_time_months = time_in_state.strftime("%m")
    current_time_days = str(int(time_in_state.strftime("%d")) + 10)
    current_time_hours = int(str(time_in_state.strftime("%H")))
    time = f'{current_time_years}-{current_time_months}-{current_time_days}T{current_time_hours}'
    past_time = f'{current_time_years}-{current_time_months}-{int(int(current_time_days) - 3)}T{current_time_hours}'
    print(current_time_hours)
    if int(current_time_hours) < 10:
            current_time_hours = f'0{current_time_hours}'
            time = f'{current_time_years}-{current_time_months}-{current_time_days}T{current_time_hours}'
            past_time = f'{current_time_years}-{current_time_months}-{int(current_time_days - 3)}T{current_time_hours}'
    # if int(current_time_days) < 10:
    #         current_time_dayss = current_time_days
    #         current_time_days = f'0{current_time_days}'
    #         time = f'{current_time_years}-{current_time_months}-{current_time_days}T{current_time_hours}'
    #         past_time = f'{current_time_years}-{current_time_months}-0{int(int(current_time_dayss) - 3)}T{current_time_hours}'
    eia_api = requests.get(f'https://api.eia.gov/v2/electricity/rto/region-data/data/?frequency=hourly&data[0]=value&facets[type][]=D&facets[respondent][]={state_eia}&start={past_time}&end={time}&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000&api_key=S0WdpfjSTJbuTuahlzvRmS8ZvW2aCoMktJvmL4E4')
    eia_api_json = eia_api.json()
    response = eia_api_json['response']['data']
    response.reverse()
    price_list = []
    for i in range(12):
        demand = response[i]['value']
        with open('./home/model_pickle', 'rb') as f:
            model = pickle.load(f)
        test = np.array([demand]).reshape((-1, 1))
        price = model.predict(test)
        price_round = round(price[0], 1)
        price_list.append(price_round)
    print(f'{state}: {price_list}')

    fig = px.line(
        x=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        y=price_list,
        labels= {'x': '', 'y': 'Price'}
    )

    fig.update_xaxes(showticklabels=False, )

    chart = fig.to_html()

    template = loader.get_template('food/past-24-hours.html')
    context = {'chart': chart, "state": state}    

    return HttpResponse(template.render(context, request))

@csrf_exempt
def next(request):
    demand = 0
    if request.method == "POST":
        things = request.POST["states"].split(" ")
        state_eia = things[1]
        state = things[2]
        if state == "NewJersey":
            state = "New Jersey"
    else:
        state_eia = "NY"
        state = "New York"

    timezone = pytz.timezone('UTC') 
    time_in_state = datetime.now(timezone)
    current_time_years = time_in_state.strftime("%Y")
    current_time_months = time_in_state.strftime("%m")
    current_time_days = str(int(time_in_state.strftime("%d")) + 10)
    current_time_hours = int(str(time_in_state.strftime("%H")))
    time = f'{current_time_years}-{current_time_months}-{current_time_days}T{current_time_hours}'
    past_time = f'{current_time_years}-{current_time_months}-{int(int(current_time_days) - 3)}T{current_time_hours}'
    print(current_time_hours)
    if int(current_time_hours) < 10:
            current_time_hours = f'0{current_time_hours}'
            time = f'{current_time_years}-{current_time_months}-{current_time_days}T{current_time_hours}'
            past_time = f'{current_time_years}-{current_time_months}-{int(current_time_days - 3)}T{current_time_hours}'
    # if int(current_time_days) < 10:
    #         current_time_dayss = current_time_days
    #         current_time_days = f'0{current_time_days}'
    #         time = f'{current_time_years}-{current_time_months}-{current_time_days}T{current_time_hours}'
    #         past_time = f'{current_time_years}-{current_time_months}-0{int(int(current_time_dayss) - 3)}T{current_time_hours}'

    print(time)
    print('4')
    eia_api = requests.get(f'https://api.eia.gov/v2/electricity/rto/region-data/data/?frequency=hourly&data[0]=value&facets[type][]=DF&facets[respondent][]={state_eia}&start={past_time}&end={time}&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000&api_key=S0WdpfjSTJbuTuahlzvRmS8ZvW2aCoMktJvmL4E4')
    # eia_api = requests.get('https://api.eia.gov/v2/electricity/rto/region-data/data/?frequency=hourly&data[0]=value&facets[respondent][]=FLA&facets[type][]=D&facets[type][]=DF&end=2023-01-25T00&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000&api_key=S0WdpfjSTJbuTuahlzvRmS8ZvW2aCoMktJvmL4E4')
    template = loader.get_template('food/next-24-hours.html')

    eia_api_json = eia_api.json()
    response = eia_api_json['response']['data']
    price_list = []
    for i in range(12):
        demand = response[i]['value']
        with open('./home/model_pickle', 'rb') as f:
            model = pickle.load(f)
        test = np.array([demand]).reshape((-1, 1))
        price = model.predict(test)
        price_round = round(price[0], 1)
        price_list.append(demand)


    print(f'{state}: {price_list}')
    fig = px.line(
        x=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        y=price_list,
        labels= {'x': '', 'y': 'Price'}
    )

    fig.update_xaxes(showticklabels=False, )

    chart = fig.to_html()


    context = {"state": state, "chart": chart}    

    return HttpResponse(template.render(context, request))





    
