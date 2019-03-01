import numpy as np
import pandas as pd
import ggplot as gg
import requests
from bs4 import BeautifulSoup
import itertools

def tofloat(string):
    if string is '':
        return 0
    return float(string)

# collect data from the bom
data = requests.get('http://www.bom.gov.au/climate/dwo/IDCJDW4019.latest.shtml')
soup = BeautifulSoup(data.text,'html.parser')
weather_observations = soup.find('table',{'summary': "Daily Weather Observations for Brisbane, Queensland for November 2018"})
tbody = weather_observations.find('tbody')

daily_min = []
daily_max = []
for tr in tbody.find_all('tr'):
    daily_min.append(tofloat(tr.find_all('td')[1].text.strip()))
    daily_max.append(tofloat(tr.find_all('td')[2].text.strip()))

# data = [[a,b] for a,b in zip(daily_min,daily_max)]

# convert from list to DataFrame
daily_temperature = pd.DataFrame(data=[[a,b,c] for a,b,c in zip(range(1,len(daily_min)+1),daily_min,daily_max)], columns=['day','daily min','daily max'])

# print(daily_temperature)

# making plots
myplot = gg.ggplot(gg.aes(x='day',y='daily_max'), data=daily_temperature) +\
    gg.geom_point()

# different way of making data frame and plots
labels = ['daily_min' for a in range(len(daily_min))] + ['daily_max' for a in range(len(daily_max))]
weather_data = pd.DataFrame(data=[[a,b,c] for a,b,c in zip(itertools.chain(range(1,len(daily_min)+1),range(1,len(daily_max)+1)),daily_min+daily_max,labels)],columns = ['day','temp','min-max'])

print(weather_data)
myplot = gg.ggplot(gg.aes(x='day',y='temp',color='min-max'), data=weather_data) +\
    gg.geom_point()

myplot.show()
