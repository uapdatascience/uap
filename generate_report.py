#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  9 18:51:43 2021

@author: uapdatascience

generate_report.py

"""

import pandas as pd
import numpy as np
import gc, copy
import getpass

def generate_all_reports(df):
    generate_simple_size_reports(df)
    generate_simple_shape_reports(df)
   
def generate_simple_size_reports(df):
    df['ufo_size'].value_counts().reset_index().to_csv('/Users/' + getpass.getuser() + '/Desktop/uap/generated_reports/size_count.csv', index=False)

    
def generate_simple_shape_reports(df):
    df['shape'].value_counts().reset_index().to_csv('/Users/' + getpass.getuser() + '/Desktop/uap/generated_reports/shape_count.csv', index=False)
    generate_shape_size_report(df)
    generate_shape_time_report(df)
    generate_shape_state_report(df)
    
def generate_shape_size_report(df): # do this by % of reports
    gr = df[df['ufo_size']!=''].groupby(['ufo_size','shape']).count()['date_posted'].reset_index()
    gr.columns = ['size','shape','count']
    
    gr2 = gr.groupby('size').agg({'count':['sum']}).reset_index()
    gr2.columns = ['size','total_count']
    gr = pd.merge(gr, gr2, how='left', on='size')
    gr['pct_cases'] = np.round(100 * gr['count'] / gr['total_count'], 2)
    gr.drop(['total_count'], axis=1, inplace=True)
    del gr2
    gc.collect()
    gr.sort_values(by=['size','count'], inplace=True, ascending=False)
    gr.to_csv('/Users/' + getpass.getuser() + '/Desktop/uap/generated_reports/most_common_shapes_by_size.csv', index=False)
    

def generate_shape_time_report(orig_df): # do this by % of reports and by decade
    df = copy.deepcopy(orig_df)
    df = df[df['date_event'] != '']
    df['decade'] = list(map(lambda dt : dt[:3] + '0s', df['date_event'].values))

    gr = df[df['ufo_size']!=''].groupby(['decade','shape']).count()['date_posted'].reset_index()
    gr.columns = ['decade','shape','count']
    
    gr2 = gr.groupby('decade').agg({'count':['sum']}).reset_index()
    gr2.columns = ['decade','total_count']
    gr = pd.merge(gr, gr2, how='left', on='decade')
    gr['pct_cases'] = np.round(100 * gr['count'] / gr['total_count'], 2)
    gr.drop(['total_count'], axis=1, inplace=True)
    del gr2
    gc.collect()
    gr.sort_values(by=['decade','count'], inplace=True, ascending=False)
    gr.to_csv('/Users/' + getpass.getuser() + '/Desktop/uap/generated_reports/most_common_shapes_by_decade.csv', index=False)

    pass

def generate_shape_state_report(orig_df): # do this by % of reports and by state
    df = copy.deepcopy(orig_df)
    df.dropna(subset=['state'], inplace=True)

    gr = df[df['ufo_size']!=''].groupby(['state','shape']).count()['date_posted'].reset_index()
    gr.columns = ['state','shape','count']
    
    gr2 = gr.groupby('state').agg({'count':['sum']}).reset_index()
    gr2.columns = ['state','total_count']
    gr = pd.merge(gr, gr2, how='left', on='state')
    
    gr = gr[gr['total_count'] > 200]
    
    gr['pct_cases'] = np.round(100 * gr['count'] / gr['total_count'], 2)
    gr.drop(['total_count'], axis=1, inplace=True)
    del gr2
    gc.collect()
    gr.sort_values(by=['state','count'], inplace=True, ascending=False)
    gr.to_csv('/Users/' + getpass.getuser() + '/Desktop/uap/generated_reports/most_common_shapes_by_state.csv', index=False)
    pass


