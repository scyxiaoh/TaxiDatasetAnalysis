
# coding: utf-8

# In[1]:


### Necessary libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import kendalltau

### Seaborn style
sns.set_style("whitegrid")


# In[2]:


### Load subway data
subway_data = pd.read_csv('NYC Subway Data/nyc-subway-turnstile-and-weather.csv')


# In[3]:


### Corralation among subway self-related features to the passenger flow volume
cor_matrix = subway_data[['ENTRIES_hourly','EXITS_hourly','day_week','weekday','rain']].corr().round(2)
fig = plt.figure(figsize=(12,12))
sns.heatmap(cor_matrix, annot=True, center=0, cmap = sns.diverging_palette(250, 10, as_cmap=True), ax=plt.subplot(111));
plt.show()


# In[4]:


### Extract the stations info
station_data = subway_data[['longitude','latitude','station']]
station_data = station_data.drop_duplicates()
station_data = station_data.sort_values(['longitude','latitude'])
station_data = station_data.reset_index(drop = True)


# In[5]:


### Add Taxi features in subway data
subway_data['Taxi_count'] = 0


# In[6]:


### Load taxi data
taxi_df = pd.read_csv('NYC Uber-Taxi Data/NYC Taxi/yellow_tripdata_2011-05.csv')


# In[ ]:


### Extract the taxi info and divide it by 4-hour time-period
df = taxi_df.set_index("pickup_datetime")
df = df[['pickup_longitude','pickup_latitude']]
df = df[((df['pickup_longitude'] < -73.7) & (df['pickup_longitude'] > -74.26)) & ((df['pickup_latitude'] > 40.49) & (df['pickup_latitude'] < 40.92))]
df = df.sort_index(ascending=True)

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days*24)):
        yield start_date + dt.timedelta(hours = n)

import datetime as dt       
matrix = []

for single_time in daterange(pd.to_datetime(df.index.min()),pd.to_datetime(df.index.max())):
    selected = df.truncate(before = single_time.strftime("%Y-%m-%d %X"), after = (single_time + dt.timedelta(seconds = 14399)).strftime("%Y-%m-%d %X"))
    matrix += [selected]


# In[ ]:


### get the nearest subway station to the taxi pickup position
import math
def nearestStation(p_long,p_lat):
    min = 1000000000
    the_station = ""
    for n in range(len(station_data.index)):
        dist = math.sqrt( (p_long - station_data['longitude'][n])**2 + (p_lat - station_data['latitude'][n])**2 )
        if (dist < min):
            min = dist
            the_station = station_data['station'][n]
    return the_station


# In[ ]:


### sort out all the taxi info to the subway station
### count how many taxi got new custumors around specific subway station
### HEAVYWORKWARNING ###
i = 0
for time_period in daterange(pd.to_datetime(df.index.min()),pd.to_datetime(df.index.max())):
    for n in range(len(matrix[i].index)):
        station_name = nearestStation(matrix[i]['pickup_longitude'].iloc[n],matrix[i]['pickup_latitude'].iloc[n])
        subway_data[(subway_data['datetime'] == time_period)&(subway_data['station'] == station_name)].Taxi_count += 1
    i += 1


# In[ ]:


### see if the subway stations (with time and weather)affect the taxi bussiness
cor_matrix = subway_data[['ENTRIES_hourly','EXITS_hourly','day_week','rain','Taxi_count']].corr().round(2)
fig = plt.figure(figsize=(12,12))
sns.heatmap(cor_matrix, annot=True, center=0, cmap = sns.diverging_palette(250, 10, as_cmap=True), ax=plt.subplot(111));
plt.show()

