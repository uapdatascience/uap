#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  6 20:50:10 2021

@author: uapdatascience

read_ufos.py

tempy_delete_this_line

https://medium.com/analytics-vidhya/how-to-generate-lat-and-long-coordinates-of-city-without-using-apis-25ebabcaf1d5

IDEAS :
craft by size
by state
by state per capita
by city
by city per capita
are crafts more likely to be seen (per capita) in less populous regions or more populous regions? does this differ by shape?
no triangles by coast or water?
within x miles of coast
within x miles of coast per capita
by time, month
predict craft by time/month/proximity to coast
clustered events by close time and/or location. same craft or different? patterns of movement?
restricted flight areas or bases?
magnetic areas?
flight paths?
weather?
credibility metric
how does size, location, duration change with time?
get % of population that lives within x miles of coast using census data and lat/long
for coast, think about hawaii and non mainland territories
what % of cities/counties/states  have > 0 reports?
weather data (clouds/storms, cold fronts, warm fronts, hurricanes, tornadoes, air pressure, wind speed and direction)
do UFOs totally avoid anywhere near an electrical storm? do they avoid certain other weather features? Could
this expose a weakness?
how does crime rate / wealth (median salary) of zip code or town affect ufo rates?
nuclear plants or other power plants
big data centers for amazon/NJ/google/etc
p test for proximity to other random points. is more likely to be close to special points vs. random ones?
first look at relationship for half of special points, see if can predict the other half!
keyword searches : (make sure to lower cap everything!, make sure this doesn't mess up numbers or special chars)
    time loss, lost time, abduction, taken, stolen, 
    coast, see, water, lake, ocean, horizon,
    starboard, seaboard, captain, log, patrol, 
    radio, photo, video
    starlink, line, string
convert both time columns to epoch seconds
typo checks : check for mispelled words by getting list of all english words then check for non numeric words
 (exclude numbers and special charachters and spaces) that are not in this english word list. Count number of types
 in each row and number of total words. 
 char length of text field as signal.
 curse words?
 python package NLP grammar and spelling
 have reliability column check 5/6 observables
 shape by time? by location? state/nuclear/military/etc?
 always check for empty spaces before and after any text!
consider time zones for reports!!!! Try to standardize to EST for everything
full vs no moon, moon cycle
light pollution map data
movement speed column (fast/slow/zip/zoom/rapid/thesaurus)
size column
impute bad event time with post date in new imputed column
ocean depth nearby? plates/trenches/materials
noise column (silent, quiet, loud, noisy, thesaurus)
for speed col, have two bool cols, fast and slow, to cover cases like "moved slowly, then zipped away"
do crafts visit same spot twice (after 1 day, week , month, year?) does this depend by shape? think about mapping,
wouldn't need to see same place twice
lots of sightings near abductions? any abduction associated shape?
cases where shape A visits and then shape B visits as a follow up? "specialist" visits after main one?

sighting by state? population adjusted?

"""

import pandas as pd
import numpy as np
import os, datetime, re, gc
from geopy import geocoders 
import getpass

def debug_helper(df):
    x = df[['date_event','date_event_orig','date_event_accurate']]
    x['length'] = x['date_event'].str.len()
    
    return x

def main():
    # first read in the file aaa
    df = pd.read_csv('/Users/' + getpass.getuser() + '/Desktop/uap/raw_data/all_nuforc_data.csv')
    df.rename(columns={'Summary':'summary','Shape':'shape', 'Duration' : 'duration', 'City':'city','State':'state'}, inplace=True)
    df['shape'] = df['shape'].str.lower()
    # now convert col formtting for Posted
    df['date_posted'] = list(map(lambda x: convert_posted(x), df['Posted'].values))
    df.drop(['Posted'], axis=1, inplace=True)
    # convert event time format
    df['Date / Time'] = df['Date / Time'].fillna(value="")
    df.rename(columns={'Date / Time' : 'date_event_orig'}, inplace=True)
    df['date_event_accurate'] = list(map(lambda x: check_convert_event_time(x), df['date_event_orig'].values))
    df['date_event'] = list(map(lambda x: convert_event_time(x), df['date_event_orig'].values))
    epoch = datetime.datetime(1970,1,1)
    time_format = "%Y-%m-%d %H:%M:%S"
    df['event_epoch'] = list(map(lambda dt, acc : 0 if not acc else int((datetime.datetime.strptime(dt, time_format) - epoch).total_seconds()), df['date_event'].values, df['date_event_accurate'].values))
    df.drop(['date_event_orig'], axis=1, inplace=True)
    # make sure the date time of the event is before or on the date posted
    df['credibility'] = np.where(df['date_posted'] + " 24:00:00" >= df['date_event'], 1, 0)
    # convert duration format
    df['duration'] = df['duration'].fillna(value="")
    df['duration_sec'] = list(map(lambda x: convert_duration(x), df['duration'].values))
    
    # make a column to tell us the size of the ufo
    df['summary'] = df['summary'].fillna(value='')
    df['summary'] = list(map(lambda summary : summary.lower(), df['summary'].values))
    df['ufo_size'] = list(map(lambda summary : get_ufo_size(summary), df['summary'].values))
    

    
    return df


def add_coordinates_into_census_data():
    df = pd.read_csv('/Users/' + getpass.getuser() + '/Desktop/uap/raw_data/census.csv')
    gn = geocoders.GeoNames("uapdatascience")
    coordinates = [0] * len(df)
    index = 0
    num_rows = len(df)
    towns = df['clean_name'].values
    states = df['state'].values
    while index < num_rows:
        if index % 100 == 0:
            print(index, ' : ', num_rows, ' : ', datetime.datetime.now())
        coordinates[index] = get_coordinates(towns[index], states[index], gn)        
        index += 1    
    df['coordinates'] = coordinates
    del coordinates, towns, states
    gc.collect()
    return df
    
def get_coordinates(town, state, gn):
    try:
        coordinates = gn.geocode("simsbury, ct")[1]
    except:
        coordinates = None
    return coordinates

def get_ufo_size(summary):
    very_big_words = ['massive','huge','mammoth','gigantic','colossal','gargantuan']
    big_words = ['big','large','great','immense']
    small_words = ['petite','small','teeny','tiny','puny','scrawny','short','mini','miniature']
    medium_words = ['medium']
    for bw in very_big_words:
        if bw in summary:
            return 'massive'
    for bw in big_words:
        if bw in summary:
            return 'big'
    for sw in small_words:
        if sw in summary:
            return 'small'
    for mw in medium_words:
        if mw in summary:
            return 'medium'
 
    return ''

def convert_duration(duration):
    duration = duration.lower()
    duration = duration.replace('one', '1')
    duration = duration.replace('two', '2')
    duration = duration.replace('three', '3')
    duration = duration.replace('few', '3')
    duration = duration.replace('several', '3')
    duration = duration.replace('couple', '2')
    duration = duration.replace('four', '4')
    duration = duration.replace('five', '5')
    duration = duration.replace('six', '6')
    duration = duration.replace('seven', '7')
    duration = duration.replace('eight', '8')
    duration = duration.replace('nine', '9')
    indices_with_digits = [duration.find(str(d)) for d in list(range(10))]
    if max(indices_with_digits) == -1:
        duration = '1' + duration
    if 'to' in duration:
        num_part = duration.split('to')[0]
    elif '-' in duration:
        num_part = duration.split('-')[0]
    elif ' ' in duration:
        indices_with_digits = [duration.find(str(d)) for d in list(range(10))]
        indices_with_digits = [ind for ind in indices_with_digits if ind >= 0]
        first_index_with_digit = min(indices_with_digits) if len(indices_with_digits) > 0 else 0
        num_part = duration[first_index_with_digit:].split(' ')[0]
    else:
        num_part = duration
    if re.sub("[^0-9]", "", num_part) == "":
        return 0
    if 'min' in duration:
        num_seconds = int(re.sub("[^0-9]", "", num_part)) * 60
    elif 'sec' in duration:
        num_seconds = int(re.sub("[^0-9]", "", num_part))
    elif 'hour' in duration or 'hr' in duration:
        num_seconds = int(re.sub("[^0-9]", "", num_part)) * 60 * 60
    else:
        num_seconds = 0
    return num_seconds

def check_convert_event_time(dt):
    if dt == "":
        return False
    if len(dt.split(' ')) == 2 and len(dt.split(' ')[1]) == 5:
        date, time_of_day = dt.split(' ')
        try:
            date = convert_posted(date)
            if '00' in date:
                return False
            return True
        except:
            return False
    elif ' ' not in dt:
        try:
            date = convert_posted(dt)
            return False
        except:
            return False
    else:
        return False
    return False

def convert_event_time(dt):
    if dt == "":
        return dt
    if len(dt.split(' ')) == 2 and len(dt.split(' ')[1]) == 5:
        date, time_of_day = dt.split(' ')
        try:
            date = convert_posted(date)
            if '00' in date:
                return ''
            return date + ' ' + time_of_day + ':00'
        except:
            return ""
    elif ' ' not in dt:
        try:
            date = convert_posted(dt)
            return date + ' ' + '00:00:00'
        except:
            return ""
    else:
        return ""
        
    
    return ""

def convert_posted(dt):
    if '?' in dt:
        return 1/0
    month, day, year = dt.split('/')
    if int(month) > 12 or int(year) > 2022 or int(day) > 31:
        return 1/0
    year = int(year)
    year = 2000 + year if year <= 21 else 1900 + year
    year = str(year)
    month = '0' + month if len(month) == 1 else month
    day = '0' + day if len(day) == 1 else day
    new_dt = year + '-' + month + '-' + day
    return new_dt