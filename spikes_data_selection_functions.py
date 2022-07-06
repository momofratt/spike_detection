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
import spikes_plot as splt

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


def get_hourly_frame(inframe, datetime_str, column_str):
    df = inframe.copy()
    df.index = df[datetime_str]
    del df[datetime_str]
    out_frame = df.resample('H').mean()
    return out_frame


def get_daily_frame(inframe, datetime_str, column_str):
    df = inframe.copy()
    df.index = df[datetime_str]
    del df[datetime_str]
    out_frame = df.resample('H').mean().resample('d').mean()
    return out_frame


def get_monthly_data(stat, id, alg, params, spec, height, years):
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
    monthly_data_diff: 2D list of float
        each list contains the montlhy mean difference between spiked and non-spiked data for the selected parameter
        the mean monthly difference is computed by averaging the hourly differences of the whole month
    """
    
    try: # if monthly tables alredy exist upload the existing tables, otherwise compute montly mean
        monthly_data_spiked_frame = pd.read_csv('./res_monthly_tables/monthly_avg_table_'     +str(stat[0:3])+'_'+str(id)+'_'+str(alg)+'_'+str(spec)+'_h'+str(height)+'.csv', sep=' ', index_col=0) 
        monthly_data_diff_frame   = pd.read_csv('./res_monthly_tables/monthly_avg_table_diff_'+str(stat[0:3])+'_'+str(id)+'_'+str(alg)+'_'+str(spec)+'_h'+str(height)+'.csv', sep=' ', index_col=0)
        monthly_data_spiked_frame.reset_index(drop=True, inplace=True) #remove first column
        monthly_data_diff_frame.reset_index(drop=True, inplace=True)
        monthly_data_spiked, monthly_data_diff = monthly_data_spiked_frame.values.tolist(), monthly_data_diff_frame.values.tolist()
        print('using existing data')  
    except:

        monthly_data = []
        monthly_data_spiked = []
        monthly_data_diff = []
        for param in params: # loop over parameter values
            in_filename = './data-minute-spiked/' + stat[0:3]+'/' + fmt.get_L1_file_name(stat[0:3], height, spec, id) +'_'+alg+'_'+param+ '_spiked'
            data = pd.read_csv(in_filename, sep=';', parse_dates=['Datetime'] )  # read dataframe with spiked data
            month_avg = []
            month_avg_spiked = []
            month_diff = []
            for year in years:
                for month in range(1,13):

                    # evaluate hourly mean difference between spiked and non-spiked data
                    month_frame = data[(data['Datetime'].dt.year == year) &
                                          (data['Datetime'].dt.month == month)]
                    month_frame_hourly = get_hourly_frame(month_frame,'Datetime',spec.lower()) # evaluate hourly mean
    
                    month_frame_spiked = data[(data['Datetime'].dt.year == year) &
                                          (data['Datetime'].dt.month == month) &
                                          (data['spike_'+spec.lower()]==False)][['Datetime', spec.lower()]] #read spiked data
                    month_frame_hourly_spiked = get_hourly_frame(month_frame_spiked, 'Datetime',spec.lower()) # evaluate hourly mean
    
                    month_frame_hourly_diff = month_frame_hourly_spiked[spec.lower()] - month_frame_hourly[spec.lower()]
    
                    month_avg.append(       round(month_frame_hourly[spec.lower()].mean(),4))
                    month_avg_spiked.append(round(month_frame_hourly_spiked[spec.lower()].mean(),4))
                    month_diff.append(      round(month_frame_hourly_diff.mean(),4))
    
            #monthly_data.append(       month_avg)
            monthly_data_spiked.append(month_avg_spiked)
            monthly_data_diff.append(  month_diff)
    
        monthly_data_spiked.append(month_avg) # append last list with no spiked data (no selection on data['spike_'+spec.lower()]==False performed)
        
        # write results to frame
        monthly_data_frame=pd.DataFrame(monthly_data_spiked)
        monthly_data_frame.columns = [str(a)+'-2019' for a in range(1,13)] + [str(b)+'-2020' for b in range(1,13)]
        monthly_data_frame.index =[alg+str(par) for par in params] + ['non-spiked']
        monthly_data_frame.to_csv('./res_monthly_tables/monthly_avg_table_'          +str(stat[0:3])+'_'+str(id)+'_'+str(alg)+'_'+str(spec)+'_h'+str(height)+'.csv', sep=' ')
    
        monthly_data_diff_frame=pd.DataFrame(monthly_data_diff)
        monthly_data_diff_frame.columns = [str(a)+'-2019' for a in range(1,13)] + [str(b)+'-2020' for b in range(1,13)]
        monthly_data_diff_frame.index =[alg+str(par) for par in params]
        monthly_data_diff_frame.to_csv('./res_monthly_tables/monthly_avg_table_diff_'+str(stat[0:3])+'_'+str(id)+'_'+str(alg)+'_'+str(spec)+'_h'+str(height)+'.csv', sep=' ')

    return monthly_data_spiked, monthly_data_diff

def get_hourly_data(stat, id, alg, params, spec, height):
    """
    read spiked data files and returns hourly averaged frame for different parameters

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
    hourly data: 2D list of float
        each list contains the hourly mean values for the selected parameter
        the last list is referred to no-spiked data
    hourly_data_diff: 2D list of float
        each list contains the hourly mean difference between spiked and non-spiked data for the selected parameter
    """
    try: # if monthly tables alredy exist upload the existing tables, otherwise compute montly mean
        hourly_data_spiked_frame = pd.read_csv('./res_hourly_tables/hourly_avg_table_'     +str(stat[0:3])+'_'+str(id)+'_'+str(alg)+'_'+str(spec)+'_h'+str(height)+'.csv', sep=' ', index_col=0) 
        hourly_data_diff_frame   = pd.read_csv('./res_hourly_tables/hourly_avg_table_diff_'+str(stat[0:3])+'_'+str(id)+'_'+str(alg)+'_'+str(spec)+'_h'+str(height)+'.csv', sep=' ', index_col=0)
        hourly_data_spiked_frame.reset_index(drop=True, inplace=True) #remove first column
        hourly_data_diff_frame.reset_index(drop=True, inplace=True)
        hourly_data_spiked, hourly_data_diff = hourly_data_spiked_frame.values.tolist(), hourly_data_diff_frame.values.tolist()
        print('using existing data at ', stat, id, alg, spec, height)  
        
    except:

        hourly_data = []
        hourly_data_spiked = []
        hourly_data_diff = []
        
        for param in params: # loop over parameter values
            in_filename = './data-minute-spiked/' + stat[0:3]+'/' + fmt.get_L1_file_name(stat[0:3], height, spec, id) +'_'+alg+'_'+param+ '_spiked'
            data = pd.read_csv(in_filename, sep=';', parse_dates=['Datetime'] )  # read dataframe with spiked data
            
            hour_frame_hourly        = get_hourly_frame(data                                    , 'Datetime',spec.lower()) # evaluate hourly mean
            hour_frame_hourly_spiked = get_hourly_frame(data[data['spike_'+spec.lower()]==False], 'Datetime',spec.lower()) # evaluate hourly mean
            
            hour_frame_hourly        = hour_frame_hourly[[spec.lower()]]
            hour_frame_hourly_spiked = hour_frame_hourly_spiked[[spec.lower()]]
            
            all_frame = hour_frame_hourly.merge(hour_frame_hourly_spiked, how='inner', left_index=True, right_index=True)
            
            hour_frame_hourly_diff = all_frame[spec.lower()+'_y'] - all_frame[spec.lower()+'_x'] # merge the two frame and compute differences between hours
    
            hour_avg        = hour_frame_hourly[spec.lower()].values.tolist()
            hour_avg_spiked = hour_frame_hourly_spiked[spec.lower()].values.tolist()
            hour_diff       = hour_frame_hourly_diff.values.tolist()                 


            hourly_data_spiked.append(hour_avg_spiked)
            hourly_data_diff.append(  hour_diff)
    
        hourly_data_spiked.append(hour_avg) # append last list with no spiked data (no selection on data['spike_'+spec.lower()]==False performed)
       
        hourly_data_frame=pd.DataFrame(hourly_data_spiked)
        #hourly_data_frame.columns = [str(a) for a in range(0,(365*2+1)*24)] 
        hourly_data_frame.index =[alg+str(par) for par in params] + ['non-spiked']
        hourly_data_frame.to_csv('./res_hourly_tables/hourly_avg_table_'          +str(stat[0:3])+'_'+str(id)+'_'+str(alg)+'_'+str(spec)+'_h'+str(height)+'.csv', sep=' ')
    
        hourly_data_diff_frame=pd.DataFrame(hourly_data_diff)
        #hourly_data_diff_frame.columns = [str(a) for a in range(0,(365*2+1)*24)] 
        hourly_data_diff_frame.index =[alg+str(par) for par in params]
        hourly_data_diff_frame.to_csv('./res_hourly_tables/hourly_avg_table_diff_'+str(stat[0:3])+'_'+str(id)+'_'+str(alg)+'_'+str(spec)+'_h'+str(height)+'.csv', sep=' ')

    return hourly_data_spiked, hourly_data_diff


def get_monthly_spike_frequency(stat, id, alg, params, spec, height, years, get_single_par_freq=False):
    """
    read spiked data files and returns monthly spike frequency frame for different parameters

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
     get_single_par_freq: bool
          choose wether to return only the output for the given params or to run all the analysis and write results on file. +
          If ==True, then the function does not write results on files and provides only the list of frequencies for the input params.
    Returns
    -------
    monthly data: 2D list of float
        each list contains the montlhy mean values for the selected parameter
        the last list is referred to no-spiked data
    monthly_data_diff: 2D list of float
        each list contains the montlhy mean difference between spiked and non-spiked data for the selected parameter
        the mean monthly difference is computed by averaging the hourly differences of the whole month
    """
    
    try: # if monthly tables alredy exist upload the existing tables, otherwise compute montly mean
        monthly_freq_frame = pd.read_csv('./res_monthly_tables/monthly_freq_table_'     +str(stat[0:3])+'_'+str(id)+'_'+str(alg)+'_'+str(spec)+'_h'+str(height)+'.csv', sep=' ', index_col=0) 
        monthly_freq_frame.reset_index(drop=True, inplace=True) #remove first column
        monthly_freq = monthly_freq_frame.values.tolist()
        #print('using existing data')  
    except:

        monthly_freq = []
        
        for param in params: # loop over parameter values

            in_filename = './data-minute-spiked/' + stat[0:3]+'/' + fmt.get_L1_file_name(stat[0:3], height, spec, id) +'_'+alg+'_'+param+ '_spiked'
            data = pd.read_csv(in_filename, sep=';', parse_dates=['Datetime'] )  # read dataframe with spiked data

            monthly_freq_line = []
            for year in years:
                for month in range(1,13):
                    # evaluate number of data and number of spikes for each month
                    ndata = len(data[(data['Datetime'].dt.year == year) &
                                          (data['Datetime'].dt.month == month)][spec.lower()])
    
                    nspikes= len(data[(data['Datetime'].dt.year == year) &
                                          (data['Datetime'].dt.month == month) &
                                          (data['spike_'+spec.lower()]==True)][spec.lower()]) #read spiked data
    
                    if ndata > 0:
                        freq = nspikes/ndata
                    else:
                        freq = np.nan
                        
                    monthly_freq_line.append( round(freq,3))
                    
            monthly_freq.append(monthly_freq_line)
        
        monthly_data_frame=pd.DataFrame(monthly_freq)
        monthly_data_frame.columns = [str(a)+'-2019' for a in range(1,13)] + [str(b)+'-2020' for b in range(1,13)]
        monthly_data_frame.index =[alg+str(par) for par in params] 
        monthly_data_frame.to_csv('./res_monthly_tables/monthly_freq_table_'          +str(stat[0:3])+'_'+str(id)+'_'+str(alg)+'_'+str(spec)+'_h'+str(height)+'.csv', sep=' ')
    
    if get_single_par_freq: # skip to except if get_single_par_freq == True
        temp_monthly_freq=[]    
        indexes = splt.get_indexes_for_monthly_boxplot(alg, params)
        for i in indexes:   
            temp_monthly_freq.append(monthly_freq[i])
        monthly_freq = temp_monthly_freq 
    return monthly_freq


def get_daily_season_data(stat, id, alg, params, spec, height,season,season_str):
    ## NB this function should be implemented with a try-except statement as for the get_monthly_data() function.
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
    try:# if daily tables alredy exist upload the existing tables, otherwise compute daily mean cycles
        daily_data_spiked_frame = pd.read_csv('./res_daily_tables/daily_cycle_table_'+str(stat)+'_'+str(alg)+'_'+str(spec)+'_h'+str(height)+'_'+season_str+'.csv', sep=' ', index_col=0) 
        daily_data_diff_frame   = pd.read_csv('./res_daily_tables/daily_cycle_table_diff_'+str(stat)+'_'+str(id)+'_'+str(alg)+'_'+str(spec)+'_h'+str(height)+'_'+season_str+'.csv', sep=' ', index_col=0)
        daily_data_spiked_frame.reset_index(drop=True, inplace=True) #remove first column
        daily_data_diff_frame.reset_index(drop=True, inplace=True)
        daily_cycles, daily_cycles_diff = daily_data_spiked_frame.values.tolist(), daily_data_diff_frame.values.tolist()
    
    
    except:
        daily_cycles=[]
        daily_cycles_diff=[]

        if season[0]<season[1]: # if the first month is december consider the previous year
            start_date = dt.datetime(2020,season[0],1)
        else:
            start_date = dt.datetime(2019,season[0],1)
        end_date = dt.datetime(2020,season[1],1)

        for param in params: # loop over parameter values
            in_filename = './data-minute-spiked/' + stat +'/' + fmt.get_L1_file_name(stat, height, spec, id) +'_'+alg+'_'+param+ '_spiked'
            data = pd.read_csv(in_filename, sep=';', parse_dates=['Datetime'] )  # read dataframe with spiked data
            season_data = data.loc[(data['Datetime'] > start_date) &
                                (data['Datetime'] < end_date) &
                                (data['spike_'+spec.lower()]==False)] # read spiked data
            season_data_hourly = get_hourly_frame(season_data, 'Datetime',spec.lower())

            season_data_non_spiked = data.loc[(data['Datetime'] > start_date) &
                                            (data['Datetime'] < end_date)] # read non-spiked data
            season_data_non_spiked_hourly = get_hourly_frame(season_data_non_spiked, 'Datetime', spec.lower())

            season_data_hourly_diff = season_data_hourly[spec.lower()] - season_data_non_spiked_hourly[spec.lower()]

            #season_data = season_data.set_index("Datetime")

            daily = []
            daily_diff = []
            for i in range(0,24):
                daily.append(     round( season_data_hourly.between_time(     str(datetime.time(i,0,0)), str(datetime.time(i,59,0)) )[spec.lower()].mean(),2) )
                daily_diff.append(round( season_data_hourly_diff.between_time(str(datetime.time(i,0,0)), str(datetime.time(i,59,0)) ).mean(),2) )

            daily_cycles.append(daily)
            daily_cycles_diff.append(daily_diff)

        # append last list with no spiked data (no selection on data['spike_'+spec.lower()]==False performed)
        daily = []
        for i in range(0,24):
            daily.append( round(season_data_non_spiked_hourly.between_time(str(datetime.time(i,0,0)), str(datetime.time(i,59,0)) )[spec.lower()].mean(),2) )
        daily_cycles.append(daily)

        daily_data_frame=pd.DataFrame(daily_cycles)
        daily_data_frame.columns = [str(a) for a in range(0,24)] 
        daily_data_frame.index =[alg+str(par) for par in params] + ['non-spiked']
        daily_data_frame.to_csv('./res_daily_tables/daily_cycle_table_'+str(stat)+'_'+str(alg)+'_'+str(spec)+'_h'+str(height)+'_'+season_str+'.csv', sep=' ')

        daily_data_diff_frame=pd.DataFrame(daily_cycles_diff)
        daily_data_diff_frame.columns = [str(a) for a in range(0,24)]
        daily_data_diff_frame.index =[alg+str(par) for par in params]
        daily_data_diff_frame.to_csv('./res_daily_tables/daily_cycle_table_diff_'+str(stat)+'_'+str(id)+'_'+str(alg)+'_'+str(spec)+'_h'+str(height)+'_'+season_str+'.csv', sep=' ')



    return daily_cycles, daily_cycles_diff

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


def write_heatmap_table_freq(stations, years, algo, spec):
        config=ConfigParser()
        alg = algo[0] # algorithm name
        parameters = algo[1:len(algo)]
        for par in parameters:
            print(alg, par)
            df = pd.DataFrame()
            indexes=[]
            for stat in stations:
                if (stat=='KIT') & (spec=='CO'):
                    stat='KIT_CO'
                if (stat=='PUI') & (spec=='CO'):
                    continue
                config.read('stations.ini') 
                heights = config.get(stat, 'height' ).split(',')
                species = config.get(stat, 'species').split(',')
                ID      = config.get(stat, 'inst_ID').split(',')
                stat = stat[0:3]
                height = heights[-1] # get higher altitude
                    
                df_stat = pd.DataFrame(get_monthly_spike_frequency(stat, ID[0], alg, [par], spec, height, years, get_single_par_freq=True))
                indexes.append(stat+'-'+ID[0])
                df = pd.concat([df, df_stat])
            df.set_index(pd.Index(indexes), inplace=True)
            df.to_csv('./heatmap_tables/heatmap_table_freq_'+str(alg)+'_'+str(par)+'_'+str(spec)+'.csv', sep = ' ')







