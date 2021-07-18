#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 18 18:18:09 2021

@author: danieldouglass

add_in_gps_coordinates.py

"""

import gc, datetime, copy, getpass
from geopy import geocoders 
import pandas as pd
import numpy as np

def add_coordinates_into_census_data(df=None, run_time_seconds=60*60*12, start_index=-1):
    
    #TO DO : " borough"
    
    #df['coordinates'] = list(map(lambda x: tuple([float(i) for i in x.replace('(','').replace(')','').split(',')]) if type(x)==str else None, df['coordinates']))
    #census['distance'] = list(map(lambda x,y : max(abs(x[0]-y[0]),abs(x[1]-y[1])) if x is not None and y is not None else 0, census['coordinates'], census['state_coordinates']))
    #clean_name     47919
    #coordinates    14324, 16602, 18356, 21237, 25953, 36770, 36771
    if df is None:
        df = pd.read_csv('/Users/' + getpass.getuser() + '/Desktop/uap/raw_data/census.csv')
        df['coordinates'] = None
        df['clean_name'] = list(map(lambda x: x[:-3] if x[-3:] == ' ut' else x, df['clean_name']))
        df['clean_name'] = list(map(lambda x: x.replace(' consolidated government','').replace(' unified government',''), df['clean_name']))
    gn = geocoders.GeoNames("uapdatascience")
    coordinates = list(df['coordinates'])
    index = 0
    num_rows = len(df)
    towns = df['clean_name'].values
    states = df['state'].values
    clock_start = datetime.datetime.now()
    time_has_run_out = False
    while (index < num_rows) and (not time_has_run_out):
        if index % 100 == 0:
            print(index, ' : ', num_rows, ' : ', datetime.datetime.now())
        if coordinates[index] is None and index > start_index:#or math.isnan(coordinates[index]): 12000
            coordinates[index] = get_coordinates(towns[index], states[index], gn)        
        index += 1    
        curr_time = datetime.datetime.now()
        if (curr_time - clock_start).total_seconds() > run_time_seconds:
            time_has_run_out = True
    df['coordinates'] = coordinates
    del coordinates, towns, states
    gc.collect()
    return df


def get_coordinates_helper(town, state, gn):
    try:
        coordinates = gn.geocode(town + ", " + state + " , usa")[1]
    except:
        coordinates = None
    return coordinates

def get_coordinates(town, state, gn):
    coordinates = get_coordinates_helper(town, state, gn)
    if coordinates is None:
        town_to_try = town[:-3] if town[-3:] == ' ut' else town
        town_to_try = town_to_try.replace(' unified government','').replace(' village','').replace(' consolidated government','').replace(' indianship','')
        town_to_try = town_to_try.replace(' consolidated','')
        coordinates = get_coordinates_helper(town_to_try, state, gn)
    if coordinates is None:
        curr_town_to_try = town_to_try.replace('-','')
        coordinates = get_coordinates_helper(curr_town_to_try, state, gn)
    if coordinates is None:
        curr_town_to_try = town_to_try.replace("'","")
        coordinates = get_coordinates_helper(curr_town_to_try, state, gn)
    if coordinates is None:
        curr_town_to_try = town_to_try.split('-')[-1]
        coordinates = get_coordinates_helper(curr_town_to_try, state, gn)
    return coordinates

if __name__ == '__main__':
    df = pd.read_csv('/Users/' + getpass.getuser() + '/Desktop/uap/raw_data/census_with_coordinates_4.csv')
    df['coordinates'] = list(map(lambda x: tuple([float(i) for i in x.replace('(','').replace(')','').split(',')]) if type(x)==str else None, df['coordinates']))
    start_index = np.random.randint(0, len(df) - 500)
    add_coordinates_into_census_data(df=df, run_time_seconds=1*60, start_index=start_index)
    df.to_csv('/Users/' + getpass.getuser() + '/Desktop/uap/raw_data/census_with_coordinates_4.csv', index=False)
    
    
    