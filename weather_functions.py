import datetime
import itertools
import json
import random
import statistics
import time
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
#import plotly
#import plotly.graph_objects as go
import seaborn as sns
import sklearn as sk
from numpy import mean
from plotly.offline import plot
from sklearn import linear_model, metrics
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import (LinearRegression, LogisticRegression,
                                  PoissonRegressor)
from sklearn.metrics import (accuracy_score, classification_report,
                             confusion_matrix, precision_score, r2_score,
                             recall_score)
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.tree import DecisionTreeClassifier

from get_information_sprottenflotte import (get_renting, get_returning,
                                            get_station_of_kiel)


# Datetime functions
def ISOtime_to_UNIX(t):
    '''converts ISOtime (weather data) to UNIX time'''
    tidt = datetime.datetime.fromisoformat(t)
    result = time.mktime(tidt.timetuple())
    return result

# function that turns UNIX time wich is in float to timestamp
# pd.to_datetime(sf_day_next['last_update'][0], unit='s')

# Function to find noise in a dataframe
def find_noise_in_timestamp(a_df):
    '''find noise in the weather data and return a cleaned dataframe '''
    list_of_noise_times = []
    copy_df = a_df[:]

    for time_sl in range(len(copy_df.index)-1):
        #sometimes there are 'hh:10' times   
        if copy_df['timestamp'][time_sl][14:16] == '10':
            #if they aren't the first time in the morning we drop them
            if copy_df['timestamp'][time_sl][11:13] != '06':
                copy_df.drop([time_sl], inplace = True)

                
            #otherwise we make them to the first time in the morning
            elif copy_df['timestamp'][time_sl][11:13] == '06':
                old_tim = copy_df['timestamp'][time_sl]
                new_tim = old_tim[0:14] + '00' + old_tim[16:]  
                copy_df.at[time_sl,'timestamp'] = new_tim
    copy_df.reset_index(drop = True, inplace = True)
 
    mutated_w_df = copy_df[:] 
    w_df = copy_df[:] 
     
    for time_slot in range(len(w_df.index)-1):        
        
        #a row is twice in the df
        if ((w_df['timestamp'][time_slot][11:13]== w_df['timestamp'][time_slot + 1][11:13]) and (w_df['timestamp'][time_slot + 1 ][14:16] != '30')): 
            list_of_noise_times.append((time_slot, w_df['timestamp'][time_slot], w_df['timestamp'][time_slot + 1], 'fall0'))
            mutated_w_df.drop([time_slot],inplace = True)  
            
        #half an hour is missing and the first one was '00' or '10' 
        elif ((int(w_df['timestamp'][time_slot][11:13])+1 == int(w_df['timestamp'][time_slot +1 ][11:13])) and (w_df['timestamp'][time_slot][14:16] == w_df['timestamp'][time_slot +1][14:16]) and (w_df['timestamp'][time_slot][14:16] == '00')) :
            list_of_noise_times.append((time_slot, w_df['timestamp'][time_slot], w_df['timestamp'][time_slot + 1], 'fall1'))

            row_copy = mutated_w_df.loc[time_slot].copy()
            mutated_w_df.loc[time_slot + 0.5] = row_copy.to_list()
                
            old_time = mutated_w_df['timestamp'][time_slot]                
            new_time = old_time[0:14] + '30' + old_time[16:]   
            mutated_w_df.at[time_slot +0.5,'timestamp'] = new_time
        
                
                
        # half an hour is missing and the first one was '30'         
        elif (((int(w_df['timestamp'][time_slot][11:13])+1 == int(w_df['timestamp'][time_slot +1 ][11:13]))) and ((w_df['timestamp'][time_slot][14:16] == w_df['timestamp'][time_slot +1][14:16])) and (w_df['timestamp'][time_slot][14:16] == '30')) :
            list_of_noise_times.append((time_slot, w_df['timestamp'][time_slot], w_df['timestamp'][time_slot + 1]))

            row_copy = mutated_w_df.loc[time_slot].copy()
            mutated_w_df.loc[time_slot+0.5] = row_copy.to_list()
                
            old_time = mutated_w_df['timestamp'][time_slot]
            new_time = old_time[0:11] + str(int(old_time[11:13])+1).zfill(2) + ':00' + old_time[16:]
            
            mutated_w_df.at[time_slot +0.5,'timestamp'] = new_time
            
        #a whole hour is missing
        elif (int(w_df['timestamp'][time_slot][11:13])+2 == int(w_df['timestamp'][time_slot +1 ][11:13])):
            
            row_copy = mutated_w_df.loc[time_slot].copy()
            mutated_w_df.loc[time_slot + 0.25] = row_copy.to_list()
            mutated_w_df.loc[time_slot + 0.5] = row_copy.to_list()
                
            old_time = mutated_w_df['timestamp'][time_slot]                
            new_time1 = old_time[0:11] + str(int(old_time[11:13])+1).zfill(2) + ':00' + old_time[16:]
            new_time2 = old_time[0:11] + str(int(old_time[11:13])+1).zfill(2) + ':30' + old_time[16:]
            
            mutated_w_df.at[time_slot + 0.25,'timestamp'] = new_time1
            mutated_w_df.at[time_slot + 0.5,'timestamp'] = new_time2
            
    mutated_w_df.sort_index(inplace = True)
    mutated_w_df = mutated_w_df.reset_index(drop = True)
                
    return list_of_noise_times, mutated_w_df

# Functions for preprocessing the bike data
def sum_up_funtion(dicto, df):
    '''sums an information like the renting numbers up from every stations and returns a list of each half hour of all stations'''
    
    list_of_all = []
    len_of_time= len(dicto[24371])
    station_id_list = df["Station_ID"].unique()
    
    for value in range(0,len_of_time):
        list =[]
        for station in station_id_list:
            if station != 26355:
                list += [dicto[station][value]]
        list_of_all.append(sum(list))
    return list_of_all


def avg_number_of_bike_per_half_hour(df):
    '''get the average number of bikes which are located at the stations per half hour '''
    
    avg_number_of_bikes = {}
    first_update = df["last_update"].values[0]
    half_hour = first_update + 1800
    station_id_list = df["Station_ID"].unique()
    last_update = df["last_update"].values[-1]
        
    for station in station_id_list:
        number_bikes_per_half_hour = []

        half_hour_copy = half_hour
        first_update_copy = first_update

        while half_hour_copy < last_update:
            if not ((station == 26355) or (first_update_copy < 1678180903 and first_update_copy > 1678168785) or (first_update_copy > 1678249874 and first_update_copy < 1678264138) or (first_update_copy < 1678906800 and first_update_copy > 1678878000) or (((pd.to_datetime(half_hour_copy, unit='s')).hour > 21) and ((pd.to_datetime(half_hour_copy, unit='s')).minute > 3)) or ((pd.to_datetime(half_hour_copy, unit='s')).hour < 6)):                                                                                                                         
                result_df = df.loc[ (df["Station_ID"] == station) & 
                                                    (df["last_update"] >= first_update_copy) & 
                                                    (df["last_update"] < half_hour_copy) ]
                entry = result_df["Number_of_Bikes"].to_list()
                number_bikes_per_half_hour.append(((sum(entry) / len(entry))))
             
            first_update_copy = half_hour_copy
            half_hour_copy += 1800
            
            if ((((pd.to_datetime(half_hour_copy, unit='s')).hour < 22) or (((pd.to_datetime(half_hour_copy, unit='s')).hour == 22) and ((pd.to_datetime(half_hour_copy, unit='s')).minute < 3))) and ((pd.to_datetime(half_hour_copy, unit = 's')).hour >= 6)):
               continue
            else:
                first_update_copy += 28800
                half_hour_copy += 28800 
                
        avg_number_of_bikes[station] = number_bikes_per_half_hour
    
    return avg_number_of_bikes


def usage_of_station_per_half_hour(df):
    '''get the number of bikes which are use at the stations per half hour'''
    usage_of_station = {}
    first_update = df["last_update"].values[0]
    half_hour = first_update + 1800
    station_id_list = df["Station_ID"].unique()
    last_update = df["last_update"].values[-1]

    for station in station_id_list:
        usage_of_station_per_half_hour = []
        
        half_hour_copy = half_hour
        first_update_copy = first_update

        while half_hour_copy < last_update:
                
            if not ((station == 26355) or (first_update_copy < 1678180903 and first_update_copy > 1678168785) or (first_update_copy > 1678249874 and first_update_copy < 1678264138) or (first_update_copy < 1678906800 and first_update_copy > 1678878000) or (((pd.to_datetime(half_hour_copy, unit='s')).hour > 21) and ((pd.to_datetime(half_hour_copy, unit='s')).minute > 3)) or ((pd.to_datetime(half_hour_copy, unit='s')).hour < 6)):                                                                                                                        
                result_df = df.loc[ (df["Station_ID"] == station) & 
                                                    (df["last_update"] >= first_update_copy) & 
                                                    (df["last_update"] < half_hour_copy) ]
                reported = result_df["last_reported"].unique()
                usage_of_station_per_half_hour.append(len(reported))


            first_update_copy = half_hour_copy
            half_hour_copy += 1800
            
            if ((((pd.to_datetime(half_hour_copy, unit='s')).hour < 22) or (((pd.to_datetime(half_hour_copy, unit='s')).hour == 22) and ((pd.to_datetime(half_hour_copy, unit='s')).minute < 3))) and ((pd.to_datetime(half_hour_copy, unit = 's')).hour >= 6)):
               continue
            else:
                first_update_copy += 28800
                half_hour_copy += 28800 
                
        usage_of_station[station] = usage_of_station_per_half_hour
    
    return usage_of_station


def returning_bike_of_station_per_half_hour(df):
    '''get the number of bikes which are returned at the stations per half hour'''
    returning_bike_of_station = {}
    first_update = df["last_update"].values[0]
    half_hour = first_update + 1800
    station_id_list = df["Station_ID"].unique()
    last_update = df["last_update"].values[-1]

    for station in station_id_list:
        number_of_bikes_returning= []
        
        half_hour_copy = half_hour
        first_update_copy = first_update

        while half_hour_copy < last_update:

                if not ((station == 26355) or (first_update_copy < 1678180903 and first_update_copy > 1678168785) or (first_update_copy > 1678249874 and first_update_copy < 1678264138)or (first_update_copy < 1678906800 and first_update_copy > 1678878000) or (((pd.to_datetime(half_hour_copy, unit='s')).hour > 21) and ((pd.to_datetime(half_hour_copy, unit='s')).minute > 3)) or ((pd.to_datetime(half_hour_copy, unit='s')).hour < 6)):                                                                                                                        
                    result_df = df.loc[ (df["Station_ID"] == station) & 
                                                    (df["last_update"] >= first_update_copy) & 
                                                    (df["last_update"] < half_hour_copy) ]
                    number_of_bikes = result_df["Number_of_Bikes"].to_list()
                    number_of_bikes_returning.append((get_returning(number_of_bikes)))
                    
                    
                first_update_copy = half_hour_copy
                half_hour_copy += 1800

                if ((((pd.to_datetime(half_hour_copy, unit='s')).hour < 22) or (((pd.to_datetime(half_hour_copy, unit='s')).hour == 22) and ((pd.to_datetime(half_hour_copy, unit='s')).minute < 3))) and ((pd.to_datetime(half_hour_copy, unit = 's')).hour >= 6)):
                    continue
                else:
                    first_update_copy += 28800
                    half_hour_copy += 28800 
                
        returning_bike_of_station[station] = number_of_bikes_returning

    return returning_bike_of_station


def renting_bike_of_station_per_half_hour(df):
    '''get the number of bikes which are rented at the stations per half hour'''
    renting_bike_of_station = {}
    first_update = df["last_update"].values[0]
    half_hour = first_update + 1800
    station_id_list = df["Station_ID"].unique()
    last_update = df["last_update"].values[-1]

    for station in station_id_list:
        number_of_bikes_renting= []

        half_hour_copy = half_hour
        first_update_copy = first_update

        while half_hour_copy < last_update:
            
                         
            if not ( (station == 26355) or (first_update_copy < 1678180903 and first_update_copy > 1678168785) or (first_update_copy > 1678249874 and first_update_copy < 1678264138) or (first_update_copy < 1678906800 and first_update_copy > 1678878000) or (((pd.to_datetime(half_hour_copy, unit='s')).hour > 21) and ((pd.to_datetime(half_hour_copy, unit='s')).minute > 3)) or ((pd.to_datetime(half_hour_copy, unit='s')).hour < 6)):                                                                                                                        
                result_df = df.loc[ (df["Station_ID"] == station) & 
                                                    (df["last_update"] >= first_update_copy) & 
                                                    (df["last_update"] < half_hour_copy) ]
                number_of_bikes = result_df["Number_of_Bikes"].to_list()
                number_of_bikes_renting.append((get_renting(number_of_bikes)))
            
            first_update_copy = half_hour_copy
            half_hour_copy += 1800
            
            if ((((pd.to_datetime(half_hour_copy, unit='s')).hour < 22) or (((pd.to_datetime(half_hour_copy, unit='s')).hour == 22) and ((pd.to_datetime(half_hour_copy, unit='s')).minute < 3))) and ((pd.to_datetime(half_hour_copy, unit = 's')).hour >= 6)):
                continue
            else:
                first_update_copy += 28800
                half_hour_copy += 28800 

        renting_bike_of_station[station] = number_of_bikes_renting

    return renting_bike_of_station

#watching some attributes together
def make_a_plot(weather_attribute, sf_attribute,df):
    '''makes a plot for one weather- and one sprottenflotte-attribute'''
    
    # make a plot with different y-axis using second axis object
    fig,ax = plt.subplots()
    ax.plot(df['timestamp'], df[weather_attribute],color="red")
    ax.set_xlabel("timestamp", fontsize = 14)
    ax.set_ylabel(str(weather_attribute),color="red",fontsize=14)
    
    ax2=ax.twinx()
    ax2.plot(df['timestamp'], df[sf_attribute],color="blue")
    ax2.set_ylabel(str(sf_attribute),color="blue",fontsize=14)
    
    plt.show()


# Prediction functions over all stations

def make_three_classes_of_rented(x):
    '''subdivides the number of rented bikes in 3 classes'''
    
    if x <= 6:
        return "low"
    elif (x > 6 and x <= 14):
        return "normal"
    elif (x > 14):
        return "high"
    
def make_a_prediction(precipitation, condition, sunshine, temperature, windspeed, model):
    '''makes prediciton with the random forest model based on the input weather data'''
    
    df = pd.DataFrame(
      {
      "Precipitation": [precipitation],
      "Condition": [condition],
      "Sunshine": [sunshine],
      "Temperature" : [temperature],
      "wind_speed": [windspeed]
      }
      )
  
    number = model.predict(df)
    return number[0]


def make_a_prediction_categories(tupl, model):
    '''translates the input values into the weather input values for 'make_a_prediction' '''
    
    preci = tupl[0]
    wind = tupl[1]
    temperature = tupl[2]
    sun = tupl[3]
    
    #sun
    if sun == 'yes':
        s = 30
    if sun == 'no':
        s=0
    
    #preci
    if preci == 'rain' and temperature == 'positive':
        c = 1
    if preci == 'rain' and temperature == 'negative':
        c = 0
    if preci == 'snow' and temperature == 'positive':
        c = 0
        p = 0.1
    if preci == 'snow' and temperature == 'negative':
        c = 1
        p = 0.1    
    if preci == 'nothing':
        c=4
        p = 0.0
    
    #wind
    if wind == 'low':
        w = 0
    if wind == 'middle':
        w= 10
    if wind == 'high':
        w = 20
        
    #temperature   
    if temperature == 'positive':
        t = 2
    if temperature == 'negative':
        t = -2
    
    return make_a_prediction(0, c, s, t, w, model)

# Prediction functions for one station

def make_three_classes_of_rented_per_station(x):
    '''subdivides the number of rented bikes in three categories'''
    if x < 1:
        return "rare"
    elif (x >= 1 and x < 4):
        return "a few times"
    elif x >= 4:
        return "more often"


def make_a_df_with_blocks_3_hours(df):
    '''aggregates the values for 3 hours '''
    
    dict_of_blocks = {'Preci':[], 'Cond':[], 'Sun':[], 'Temp':[], 'wind':[], 'rented':[]}
    list_prec = df['Precipitation'].to_list()
    list_cond = df['Condition'].to_list()
    list_sun = df['Sunshine'].to_list()
    list_temp = df ['Temperature'].to_list()
    list_wind = df['wind_speed'].to_list()
    list_bikes = df['rented bikes'].to_list()

    while list_prec:
        if len(list_prec) >5:
            dict_of_blocks['Preci'].append(mean(list_prec[0:7]))
            list_prec =list_prec[7:]
        else:
            dict_of_blocks['Preci'].append(mean(list_prec))
            list_prec =[]
  
    while list_cond:
        if len(list_cond) >5:
            dict_of_blocks['Cond'].append(int(mean(list_cond[0:7])))
            list_cond =list_cond[7:]
        else:
            dict_of_blocks['Cond'].append(int(mean(list_cond)))
            list_cond =[]  
    
    while list_sun:
        if len(list_sun) >5:
            dict_of_blocks['Sun'].append(mean(list_sun[0:7]))
            list_sun =list_sun[7:]
        else:
            dict_of_blocks['Sun'].append(mean(list_sun))
            list_sun =[]   
            
    while list_temp:
        if len(list_temp) >5:
            dict_of_blocks['Temp'].append(mean(list_temp[0:7]))
            list_temp =list_temp[7:]
        else:
            dict_of_blocks['Temp'].append(mean(list_temp))
            list_temp =[] 
    
    while list_wind:
        if len(list_wind) >5:
            dict_of_blocks['wind'].append(mean(list_wind[0:7]))
            list_wind =list_wind[7:]
        else:
            dict_of_blocks['wind'].append(mean(list_wind))
            list_wind =[] 
            
    while list_bikes:
        if len(list_bikes) >5:
            dict_of_blocks['rented'].append(sum(list_bikes[0:7]))
            list_bikes =list_bikes[7:]
        else:
            dict_of_blocks['rented'].append(sum(list_bikes))
            list_bikes =[] 
    
    return pd.DataFrame.from_dict(dict_of_blocks)


kiel_station = [24371, 24384, 24468, 24385, 26209, 26224, 26262, 24412, 24376,
       24397, 24383, 24387, 24413, 24389, 24466, 24398, 24380, 24401,
       24454, 24375, 24480, 24381, 24436, 24476, 24399, 24447, 24400,
       24378, 24370, 24407, 24394, 24453, 24392, 24391, 24477, 24415,
       24395, 24406, 24408, 24474, 24382, 24367, 24473, 24386, 24388,
       24405, 24410, 24404, 24414, 24442, 24440, 24448, 24449, 24469,
       24368, 24393, 24409, 24373, 24390, 24411, 24441, 24417, 24377,
       24419, 24403, 24369, 24374, 24481, 24450, 24379, 24471, 24372,
       24465, 24467, 24396, 24457, 24416, 24402]

def make_dataframe_of_weather_and_sf_per_station(station, df_w_s, dict1):
    '''makes a dataframe with the weather and bike dates for a certain station'''

    df_w_s['rented bikes'] = dict1[station]

    
    return df_w_s


def make_model_based_on_station_pr(station, df_w_s, dict1):
    ''' trains a Poisson Regressor model based on the data of a certain station'''
    df = make_a_df_with_blocks_3_hours(make_dataframe_of_weather_and_sf_per_station(station, df_w_s, dict1))
    
    df['rented bikes class'] = df['rented'].to_list()
    df['rented bikes class'] = df['rented bikes class'].apply(make_three_classes_of_rented_per_station)
    
    xss = df.iloc[:,0:5]
    yss = df.iloc[:,5]
    
    xss_train,xss_test,yss_train,yss_test = train_test_split(xss, yss, test_size = 0.3, random_state = 42)

    rfss = PoissonRegressor()
    rfss.fit(xss, yss)
    
    return rfss


def make_prediction_based_on_station(stat, tuple, df_w_s, dict1):
    '''makes a prediction based on a station and a qunituple of the weather conditions''' 
    pre = tuple[0]
    con = tuple[1]
    sun = tuple[2]
    temp = tuple[3]
    wind = tuple[4]
     
    df2 = pd.DataFrame(
        {
        "Preci": [pre],
        "Cond": [con],
        "Sun": [sun],
        "Temp" : [temp],
        "wind": [wind]
        }
    )
    model = make_model_based_on_station_pr(stat, df_w_s, dict1)
    result_stat = model.predict(df2)
    
    return result_stat[0]


def make_predi_for_all_stations(tupl, df_w_s, dict1):
    '''make a prediction based on a weather quintuple for all stations'''
    
    dict_of_stations = {}
    
    for s in kiel_station:
        dict_of_stations[s] = (int(make_prediction_based_on_station(s,tupl, df_w_s, dict1)))
        
    return dict_of_stations  


def make_a_prediction_categories_stations(tupl, df_w_s, dict1):
    '''translates the input values into the weather input values for 'make_a_prediction' '''
    
    preci = tupl[0]
    wind = tupl[1]
    temperature = tupl[2]
    sun = tupl[3]
    
    #sun
    if sun == 'yes':
        s = 30
    if sun == 'no':
        #s = random.randint(0, 5)
        s=0
    
    #preci
    if preci == 'rain' and temperature == 'positive':
        c = 1
    if preci == 'rain' and temperature == 'negative':
        c = 0
    if preci == 'snow' and temperature == 'positive':
        c = 0
        p = 0.1
    if preci == 'snow' and temperature == 'negative':
        c = 1
        p = 0.1    
    if preci == 'nothing':
        #c = random.randint(3,4)
        c=4
        p = 0.0
    
    #wind
    if wind == 'low':
        #w = random.randint(0,9)
        w = 0
    if wind == 'middle':
        #w = random.randint(10,25)
        w= 10
    if wind == 'high':
        #w = random.randint(19,40)
        w = 30
        
    #temperature   
    if temperature == 'positive':
        #t = random.randint(0,5)
        t = 2
    if temperature == 'negative':
        #t = random.uniform(-2,-0.1)
        t = -2
    
    return make_predi_for_all_stations((0, c, s, t, w), df_w_s, dict1)



