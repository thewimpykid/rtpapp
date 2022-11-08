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



# Create your views here.
def index(request):
    newYorkTz = pytz.timezone("America/New_York") 
    timeInNewYork = datetime.now(newYorkTz)
    now = datetime.now()
    current_time_hours = int(timeInNewYork.strftime("%H"))
    current_time_minutes = int(timeInNewYork.strftime("%M"))
    h = current_time_hours
    m = current_time_minutes
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

    fig = px.bar(x=new_times,y=fiveminfeed_dict_recent, labels={'x':"Time", 'y':"Cents Per Kwh"}, width=350, height=300)
    chart = fig.to_html()
    # initialize var
    total = 0
    i=0
    # make requests
    reqFiveMinuteFeed = requests.get('https://hourlypricing.comed.com/api?type=5minutefeed')
    reqcurrent = requests.get('https://hourlypricing.comed.com/api?type=currenthouraverage')
    # turn requests into json
    reqcurrent_json = reqcurrent.json()
    reqFiveMinuteFeed_json = reqFiveMinuteFeed.json()
    # get current price
    currentPrice = reqcurrent_json[0]["price"]
    # get current time
    currentTime = reqcurrent_json[0]["millisUTC"]
    print(currentPrice,',',currentTime)
    # get fiveminfeed
    fiveminfeed_dict = []
    for feed in reqFiveMinuteFeed_json:
        fiveminfeed_dict.append(feed['price'])
    # get average for past 24 hours
    for item in fiveminfeed_dict:
        total += float(item)
    avg_past24hours = round(total / len(fiveminfeed_dict), 2)
    # compare results and make a rating
    rating = 5*(float(currentPrice)/avg_past24hours)
    for x in range(2):
        rating = round(rating * (float(currentPrice)/avg_past24hours), 1)

    template = loader.get_template('food/index.html')
    USDPMF = round(float(currentPrice) * 0.16, 2)
    USDPMW = round(float(currentPrice) * 1.2, 2)
    USDPMC = round(float(currentPrice) * 0.90, 2)


  
    context = {
        'USDPM': currentPrice,
        'USDPMF': USDPMF,
        'rating': rating,
        'USDPMC': USDPMC,
        'USDPMW': USDPMW,
        'chart': chart
    }
 
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
    for i in range(13):
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
        'chart2': chart2
    }

    return HttpResponse(template.render(context, request))

def next(request):
    return HttpResponse('hi')





    
