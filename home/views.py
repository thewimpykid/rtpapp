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
    reqFiveMinuteFeed = requests.get('https://hourlypricing.comed.com/api?type=5minutefeed')
    reqcurrent = requests.get('https://hourlypricing.comed.com/api?type=currenthouraverage')
    # turn requests into json

    # get current price
    print('3')
    timezone = pytz.timezone('UTC') 
    time_in_state = datetime.now(timezone)
    current_time_years = time_in_state.strftime("%Y")
    current_time_months = time_in_state.strftime("%m")
    current_time_days = (int(time_in_state.strftime("%d")) + 1)
    current_time_hours = str(int(time_in_state.strftime("%H")))
    time = f'{current_time_years}-{current_time_months}-{current_time_days}T{current_time_hours}'
    past_time = f'{current_time_years}-{current_time_months}-{int(current_time_days - 3)}T{current_time_hours}'
    print(time)
    print('4')
    eia_api = requests.get(f'https://api.eia.gov/v2/electricity/rto/region-data/data/?frequency=hourly&data[0]=value&facets[type][]=D&facets[type][]=DF&facets[respondent][]={state_eia}&start={past_time}&end={time}&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000&api_key=S0WdpfjSTJbuTuahlzvRmS8ZvW2aCoMktJvmL4E4')
    print('request done')
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

def past(request):
    reqcurrent = requests.get('https://hourlypricing.comed.com/api?type=currenthouraverage')
    reqcurrent_json = reqcurrent.json()
    currentPrice = reqcurrent_json[0]["price"]
    b=0
    newYorkTz = pytz.timezone("America/New_York") 
    timeInNewYork = datetime.now(newYorkTz)
    now = datetime.now()
    current_time_hours = int(timeInNewYork.strftime("%H"))
    current_time_minutes = int(timeInNewYork.strftime("%M"))
    h = current_time_hours
    m = current_time_minutes
    
    hours = []
    hourlyPrices = []
    times = []
    times.append(f"{current_time_hours}:{current_time_minutes}")
    i=0
    fiveminfeed_dict_recent = []
    reqFiveMinuteFeed = requests.get('https://hourlypricing.comed.com/api?type=5minutefeed')
    reqFiveMinuteFeed_json = reqFiveMinuteFeed.json()
    fiveminfeed_dict = []
    for feed in reqFiveMinuteFeed_json:
        fiveminfeed_dict.append(float(feed['price']))

    for feed in fiveminfeed_dict:
        i+=1
        if i < 11:
            fiveminfeed_dict_recent.append(feed)
    for i in range (9):
        if m < 0:
            times.append(f"{h-1}:55")
            m=55
            h-=1
            m-=5
        elif m > 60:
            times.append(f"{h-1}:00")
            m=0
            h-=1
        elif m <10:
            times.append(f'{h}: 0{m}')
            m-=5
        else:
            times.append(f'{h}:{m}')
            m-=5
    new_times = times[::-1]

    hours.append(f'{current_time_hours}: {current_time_minutes}')
    hourlyPrices.append(currentPrice)
    for i in range(12):
        if int(current_time_minutes) < 10:
            hours.append(f'{current_time_hours}: 0{current_time_minutes}')
            hourlyPrices.append(fiveminfeed_dict[i*12])
            current_time_hours -= 1
        if int(current_time_hours) < 0:
            hours.append(f'{11}: {current_time_minutes}')
            hourlyPrices.append(fiveminfeed_dict[i*12])
            current_time_hours = 11

        else:
            hours.append(f'{current_time_hours}: {current_time_minutes}')
            hourlyPrices.append(fiveminfeed_dict[i*12])
            current_time_hours -= 1
    
    fig = px.bar(x=new_times,y=fiveminfeed_dict_recent, labels={'x':"Time", 'y':"Cents Per Kwh"}, width=350, height=300)
    chart = fig.to_html()

    fig2 = px.bar(x=hours[::-1],y=hourlyPrices[::-1], labels={'x':"Time", 'y':"Cents Per Kwh"}, width=350, height=300)
    chart2 = fig2.to_html()


    length = len(hourlyPrices)

    

    template = loader.get_template('food/past-24-hours.html')

    context = {
        'chart': chart,
        'hours': hours,
        'hourlyPrices': hourlyPrices,
        'length': length,
        'chart2': chart2,
    }

    return HttpResponse(template.render(context, request))

def next(request):
    return HttpResponse('hi')





    
