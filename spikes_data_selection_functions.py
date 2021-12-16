#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 11:38:32 2021

@author: Cosimo Fratticioli
@contact: c.fratticioli@isac.cnr.it
"""
import spikes_formatting_functions as fmt
import pandas as pd
import datetime
import datetime as dt 
from configparser import ConfigParser
import numpy as np

def select_year(df, year):
    """ select one year of data
    
    Parameters
    df: DataFrame
        input dataframe 
    year: int 
        year to perform the selection
    
    Returns
    out_df:
        output dataframe
    """
    out_df = df[(df['Datetime'].dt.year==year)]
    return out_df
    
def select_month(df, year, month):
    """ select one month of data
    
    Parameters
    ----------
    df: dataframe 
    year, month: year and month to perform the selection
    
    Returns
    -------
    out_df
    """
    
    out_df = df[(df['Datetime'].dt.year==year) & (df['Datetime'].dt.month==month)]
    return out_df

def select_event(df, start_date, end_date):
    """
    select an event for plotting
    Parameters
    ----------
    df : Dataframe
        input dataframe
    start_date, end_date : datetime65
        start and end date for the selection
    Returns
    -------
    out_df : Dataframe
    """
    out_df = df[(df['Datetime'].date > start_date) & (df['Datetime'].date < end_date)]
    return out_df

def add_spike_cols(df, species):
    """
    add a bool column indicating spikes for each specie

    Parameters
    ----------
    df : DataFrame
        input dataframe with 'SpeciesList' column
    species: list
        list of strings with species names

    """
    for spec in species:
        df.insert(len(df.columns), 'spike_'+spec.lower(), False)
    
    for i, row in df.iterrows():
        spikes = df.loc[i,'SpeciesList'].split(',')
        for spec in species:
                if (spec.lower() in spikes):
                    df.loc[i, 'spike_'+spec.lower()] = True

def add_spike_cols_PIQc(df, specie):
    """
    add a bool column indicating spikes for each specie in the PIQc data files

    Parameters
    ----------
    df : DataFrame
        input dataframe with 'SpeciesList' column
    species: str
        specie 

    """  
    df.insert(len(df.columns), 'spike_'+specie.lower()+'_PIQc', False)
    
    for i, row in df.iterrows():
        manual_flags = df.loc[i,'ManualDescriptiveFlag'].split(',')
        if (('Z' in manual_flags)|('Z-1' in manual_flags)|('Z-2' in manual_flags)):
            df.loc[i, 'spike_'+specie.lower()+'_PIQc'] = True

def get_monthly_data(stat, id, alg, params, spec, height,years):
    """
    read spiked data files and returns montly averaged frame for different parameters

     Parameters
     ----------

     stat, spec, id: str
         details for station name, instrument id, chemical specie from the ini file
     alg: str
         current algorithm ('SD' or 'REBS')
     params: list of str
         list of parameter values
     height: str
          sampling height
    Returns
    -------
    monthly data: 2D list of float
        each list contains the montlhy mean values for the selected parameter
        the last list is referred to no-spiked data

    """
    monthly_data = []
    for param in params: # loop over parameter values
        in_filename = './data-minute-spiked/' + stat +'/' + fmt.get_L1_file_name(stat, height, spec, id) +'_'+alg+'_'+param+ '_spiked'
        data = pd.read_csv(in_filename, sep=';', parse_dates=['Datetime'] )  # read dataframe with spiked data
        month_avg = []
        for year in years:
            for month in range(1,13):    
                month_avg.append(data[(data['Datetime'].dt.year == year) &
                                      (data['Datetime'].dt.month == month) &
                                      (data['spike_'+spec.lower()]==False)][spec.lower()].mean())
        monthly_data.append(month_avg)
    
    month_avg = []
    for year in years:
       for month in range(1,13): # append last list with no spiked data (no selection on data['spike_'+spec.lower()]==False performed)
            month_avg.append(data[(data['Datetime'].dt.year == year) &    
                                  (data['Datetime'].dt.month == month)][spec.lower()].mean())
    
    monthly_data.append(month_avg)
    monthly_data_frame=pd.DataFrame(monthly_data)
    monthly_data_frame.to_csv('./res_monthly_tables/monthly_avg_table_'+str(stat)+'_'+str(alg)+'_'+str(spec)+'_h'+str(height)+'.csv', sep=' ')
    return monthly_data

def get_daily_season_data(stat, id, alg, params, spec, height,season):
    """
    read spiked data files and returns daily cycle averaged over season for different parameters

     Parameters
     ----------
     data, spike_data: list of Dataframes
         data to be plotted. If len(data)>1 then more histograms are plotted.
     stat, spec, id: str
         details for station name, instrument id, chemical specie from the ini file
     alg: str
         current algorithm ('SD' or 'REBS')
     params: list of str
         list of parameter values
     height: str
          sampling height
    Returns
    -------
    monthly data: 2D list of float
        each list contains the montlhy median values for the selected parameter
        the last list is referred to no-spiked data

    """
    daily_cycles=[]
    for param in params: # loop over parameter values
        in_filename = './data-minute-spiked/' + stat +'/' + fmt.get_L1_file_name(stat, height, spec, id) +'_'+alg+'_'+param+ '_spiked'
        data = pd.read_csv(in_filename, sep=';', parse_dates=['Datetime'] )  # read dataframe with spiked data
        
        if season[0]<season[1]: # if the first month is december consider the previous year
            start_date = dt.datetime(2020,season[0],1)
        else:
            start_date = dt.datetime(2019,season[0],1)
        end_date = dt.datetime(2020,season[1],1)
        
        season_data = data.loc[(data['Datetime'] > start_date) &  
                        (data['Datetime']<end_date) &
                        (data['spike_'+spec.lower()]==False)]
        
        season_data = season_data.set_index("Datetime")
        daily = []
        for i in range(0,24):
            daily.append( season_data.between_time(str(datetime.time(i,0,0)), str(datetime.time(i,59,0)) )[spec.lower()].mean() )
        
        daily_cycles.append(daily)
    
    # append last list with no spiked data (no selection on data['spike_'+spec.lower()]==False performed)
    season_data = data.loc[(data['Datetime'] > start_date) & 
                           (data['Datetime']<end_date)]
    
    season_data = season_data.set_index("Datetime")
    daily = []
    for i in range(0,24):
        daily.append( season_data.between_time(str(datetime.time(i,0,0)), str(datetime.time(i,59,0)) )[spec.lower()].mean() )
    
    daily_cycles.append(daily)
    
    return daily_cycles

def write_heatmap_table(stations, years, algo, spec):
        config=ConfigParser()
        alg = algo[0] # algorithm name
        parameters = algo[1:len(algo)]
        for par in parameters:
            print(alg, par)
            df = pd.DataFrame()
            for stat in stations:
                config.read('stations.ini') 
                heights = config.get(stat, 'height' ).split(',')
                species = config.get(stat, 'species').split(',')
                ID      = config.get(stat, 'inst_ID').split(',')
                stat = stat[0:3]
                height = heights[-1] # get higher altitude
                if spec in species: # append row only if spec is in the species of the station in the ini-file. Otherwise can not open the file with (get_monthly_data)
                    season = get_monthly_data(stat, ID[0], alg, [par], spec, height, years)
                    delta = pd.Series(season[0])-pd.Series(season[1])
                    delta.name = stat
                #else:
                #    delta = pd.Series(0, index=df.columns)
                #    delta.name = stat
                df = pd.concat([df, delta.to_frame().T])

            df.to_csv('./heatmap_tables/heatmap_table_'+str(alg)+'_'+str(par)+'_'+str(spec)+'.csv', sep = ' ')










