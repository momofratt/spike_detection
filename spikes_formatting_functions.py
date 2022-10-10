#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 17:16:19 2021

@author: Cosimo Fratticioli
@contact: c.fratticioli@isac.cnr.it
"""
import pandas as pd
from configparser import ConfigParser
import spikes_data_selection_functions as sel
import datetime as dt
import numpy as np
from os import path

analyzed_months_dict = {'PUI': ['2019-1', '2020-6'], 
                        'JUS':['2019-7','2020-3'], 
                        'UTO':['2019-4', '2020-6'], 
                        'CMN':['2019-9','2020-8'], 
                        'IPR':['2019-4','2020-7']}

# IPR: APR 2019, JUL 2020, FEB 2020.
# JFJ: APR 2019, JUL 2020, NOV 2020.
# KIT: MAR 2019 (Inst: 489), JUL19 (Inst: 458)
# SAC (Inst 395): JUL 2019, MAR 2020
# JUS: JUL 2019, MAR 2020
# UTO: APR 2019, JUN 2020
# CMN: SEP 2019, NOV 2020, AUG 2020



def get_month_str(month_number):
    """ get month string from a given month number """
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September','October', 'November', 'December']
    return months[month_number-1]

def get_meas_unit(spec):
    """
    get measurement unit for a given specie
    """
    if (spec == 'CO') | (spec == 'CH4'):
        unit = '[ppb]'
    elif spec == 'CO2':
        unit = '[ppm]'

    return unit

def get_L1_file_path(station):
    """
    get path to data file

    Parameters
    ----------
    station : str
        station name with upper case. e.g. 'CMN', 'SAC'

    Returns
    -------
    file path: str

    """
    file_path = './data-minute/'+station[0:3] + '-minute-data/'
    return file_path

def get_L1_file_name(station, height, specie, inst_ID):
    """
    get file name

    Parameters
    ----------
    station : str
        station name with upper case. e.g. 'CMN', 'SAC'
    height : str
        sampling height above ground with one zero after the point: e.g 60.0
    specie : str
        chemicas specie with upper case e.g. 'CO', 'CH4'
    inst_ID: str
        instrument id
    Returns
    -------
    file_nm: str
        file name

    """
    # example for filename: IPR_2019-01-01T00:00:00_2020-12-31T23:59:58_60.0_619_C_minute.CO2
    print(station, height, specie, inst_ID)
    file_nm = station[0:3]+'_2019-01-01T00:00:00_2020-12-31T23:59:58_'+height+'_'+inst_ID+'_C_minute.'+specie
    if station[0:3]=='PDM':
        file_nm = station[0:3]+'_2014-11-01T00:00:00_2015-12-31T23:59:58_'+height+'_'+inst_ID+'_C_minute.'+specie
        
    if station[0:3]=='ZSF':
        file_nm = station[0:3]+'_2021-01-01T00:00:00_2022-05-27T23:59:58_'+height+'_'+inst_ID+'_C_minute.'+specie        

    return file_nm

def get_spike_file_path(method, param):
    """
    get path to data file

    Parameters
    ----------
    method, param : str
        spike detection method and parameter value. e.g. method = SD, param = 2.0

    Returns
    -------
    file path: str

    """
    if method == 'SD':
        file_path = './data-spikes/SD-results/SD-'+param+'/'
        if param == 'current':
            file_path = './data-spikes/SD-results/SD-currentParameters'
    if method == 'REBS':
        file_path = './data-spikes/REBS-results/REBS-'+param+'/'

    if param =='current':
        file_path = './data-spikes/SD-currentParameters/'

    return file_path

def get_spike_file_name(station, param, method, inst_ID):
    """
    get file name

    Parameters
    ----------
    station : str
        station name with upper case. e.g. 'CMN', 'SAC'
    param: str
        value of the alpha or beta parameter (according to the spike detection algorithm)
    inst_ID: str
        instrument id
    Returns
    -------
    file_nm: str
        file name
    """
    single_instrument_stations = ['CMN', 'IPR','PUI','PDM'] #stations with single instruments have no inst_ID in the datafile
    # example for filename: JFJ-226-0.1.spikes
    if method == 'SD':
        if (station in single_instrument_stations):
            file_nm = station.upper()+'-'+param+'.spikes'
        else:
            file_nm = station.upper()+'-'+inst_ID+'-'+param+'.spikes'

        if param =='current':
            file_nm = station.upper()+'_2019-01-01T00:00_2020-12-31T23:59_spike_C.Classification'
    else:
        file_nm = station.upper()+'-'+inst_ID+'-'+param+'.spikes'
    return file_nm

def read_L1_ICOS(station, height, specie, inst_ID):
    """ 
    get file path and file name and read L1 ICOS data returning a dataframe 
        Parameters
    ----------
    station : str
        station name with upper case. e.g. 'CMN', 'SAC'
    height : str
        sampling height above ground with one zero after the point: e.g 60.0
    specie : str
        chemicas specie with upper case e.g. 'CO', 'CH4'
    inst_ID: str
        instrument id
    Returns
    -------
    out_frame: DataFrame
        frame with read data

    """
    file_path = get_L1_file_path(station)
    file_name = get_L1_file_name(station, height, specie, inst_ID)
    # ####  get header nlines  ####
    file = open(file_path+file_name, 'r')
    for i in range(5): 
        line = file.readline() # read the 5th line to get the header lines number
    head_nlines = int(line.split(' ')[3]) # get the number of header lines
    file.close()
    # #### #### #### #### #### ####
    ucols = ['Year','Month','Day','Hour','Minute',specie.lower(),'Stdev', 'Flag', 'InstrumentId'] # cols to be read
    out_frame = pd.read_csv(file_path+file_name, 
                            sep=';', 
                            skiprows = head_nlines-1,
                            usecols=ucols
                            )
    insert_datetime_col(out_frame, pos=1, Y='Year',M='Month',D='Day',h='Hour',m='Minute') # insert datetime

    out_frame = out_frame[(out_frame['Flag']!='N')&
                          (out_frame['Flag']!='K')&
                          (out_frame['Flag']!='H')] # retain only data that are flagged as valid

    return out_frame

def read_L1_ICOS_PIQc(station, height, specie, inst_ID):
    """ 
    get file path and file name and read L1 ICOS data after PIQc returning a dataframe 
        Parameters
    ----------
    station : str
        station name with upper case. e.g. 'CMN', 'SAC'
    height : str
        sampling height above ground with one zero after the point: e.g 60.0
    specie : str
        chemicas specie with upper case e.g. 'CO', 'CH4'
    inst_ID: str
        instrument id
    Returns
    -------
    out_frame: DataFrame
        frame with read data

    """
    file_path = './data-minute-spiked-PIQc/'+station + '-MinuteDataAfterPIQc/'
    file_name = get_L1_file_name(station, height, specie, inst_ID)
    # ####  get header nlines  ####
    file = open(file_path+file_name, 'r')
    for i in range(5): 
        line = file.readline() # read the 5th line to get the header lines number
    head_nlines = int(line.split(' ')[3]) # get the number of header lines
    file.close()
    # #### #### #### #### #### ####
    ucols = ['Year','Month','Day','Hour','Minute','Flag','ManualDescriptiveFlag'] # cols to be read
    out_frame = pd.read_csv(file_path+file_name, 
                            sep=';', 
                            skiprows = head_nlines-1,
                            usecols=ucols,
                            converters ={'ManualDescriptiveFlag': str}
                            )
    insert_datetime_col(out_frame, pos=1, Y='Year',M='Month',D='Day',h='Hour',m='Minute') # insert datetime

    out_frame = out_frame[(out_frame['Flag']!='N')&
                          (out_frame['Flag']!='K')&
                          (out_frame['Flag']!='H')] # retain only data that are flagged as valid

    return out_frame

def read_spike_file(method, parameter, station, height, inst_ID):

    file_path = get_spike_file_path(method, parameter)
    file_name = get_spike_file_name(station, parameter, method, inst_ID)
    ucols = ['Year','Month','Day','Hour','Minute','InstrumentIds','SamplingAltitude','SpeciesList'] # cols to be read
    out_frame = pd.read_csv(file_path+file_name, 
                            sep=';', 
                            usecols=ucols
                            )
    insert_datetime_col(out_frame, pos=1, Y='Year',M='Month',D='Day',h='Hour',m='Minute') # insert datetime
    out_frame = out_frame[out_frame['InstrumentIds']==int(inst_ID)] # select only rows relative to the instrument ID
    out_frame = out_frame[out_frame['SamplingAltitude']==float(height)] # select only rows relative to the selected height
    return out_frame

def write_spiked_file(stations, alg, param):
    """
    write minute data files, select columns of interest, select flagged data and add a boolean spike column with the reported spikes.

    Parameters
    ----------
    stations : list
        list of string containing the stations names in upper case.
    alg: str
        spike algorithm name ('SD' or 'REBS')
    param: str
        value of the algorithm param. 
    Returns
    -------
    None.

    """
    config = ConfigParser()
    for stat in stations:
        config.read('stations.ini')
        heights = config.get(stat, 'height' ).split(',')
        species = config.get(stat, 'species').split(',')
        ID      = config.get(stat, 'inst_ID').split(',')
        stat=stat[0:3] # check used to read also ini file with KIT_CO that is used to read CO data at KIT. In fact CO data use different instruments and a different station has to be defined in the ini file
        for inst_id in ID:
            more_inst_id = inst_id.split('+') # used to read one datafile for each instrument and provide a single output file            
           
            for h in heights:
                for spec in species: 
                    out_frame=pd.DataFrame()
                    print(stat, inst_id, alg, param, spec, h)
                    for id in more_inst_id:  # loop over different instrument. For each instrument merge the respective spike frame, then append all the frames in a single frame
                        spike_frame = read_spike_file(alg, param, stat.upper(), h, id)
                        sel.add_spike_cols(spike_frame, [spec.lower()])
                        ####### to be improved:
                        #check_id_height(spike_frame, id, h)  
                        tmp_frame = read_L1_ICOS(station=stat, height=h, specie=spec, inst_ID=id)
                        tmp_frame = tmp_frame.merge(spike_frame[['Datetime','spike_'+spec.lower()]], how = 'left', on ='Datetime').fillna(False) # add spike column with True values corresponding to spikes
                        out_frame = out_frame.append(tmp_frame) # append the last instrument frame to the dataframe

                    out_frame.sort_values(by='Datetime', inplace=True)
                    out_filename = './data-minute-spiked/' + stat +'/' + get_L1_file_name(stat, h, spec, inst_id)+'_'+ alg +'_'+ param + '_spiked' # write "spiked" dataframe on file
                    out_frame.to_csv(out_filename, sep=';', index=False)

def add_PIQc_column(stations, alg, param):
    """
    add the column with the results of spike detection by PIs to the spiked data

    Parameters
    ----------
    stations : list
        list of string containing the stations names in upper case.
    alg: str
        spike algorithm name ('SD' or 'REBS')
    param: str
        value of the algorithm param. 
    Returns
    -------
    None.
    """
    config = ConfigParser()
    for stat in stations:
        config.read('stations.ini')
        heights = config.get(stat, 'height' ).split(',')
        species = config.get(stat, 'species').split(',')
        ID      = config.get(stat, 'inst_ID').split(',')
        stat=stat[0:3] # used to read also ini file with KIT_CO that is used to read CO data at KIT. In fact CO data use different instruments and a different station has to be defined in the ini file
        for inst_id in ID:
            more_inst_id = inst_id.split('+') # used to read one datafile for each instrument and provide a single output file            
            for h in heights:
                for spec in species: 
                    print(stat, inst_id, alg, param, spec, h)
                    frame_spiked=pd.DataFrame()
                    #for id in more_inst_id:
                    infile_spiked = './data-minute-spiked/' + stat +'/' + get_L1_file_name(stat, h, spec, inst_id)+'_'+ alg +'_'+ param + '_spiked' # write "spiked" dataframe on file
                    frame_spiked = frame_spiked.append(pd.read_csv(infile_spiked, sep=';'))

                    frame_spiked['Datetime'] = pd.to_datetime(frame_spiked['Datetime'])
                    frame_PIQc_sel = pd.DataFrame()
                    if not path.exists(infile_spiked + '_PIQc'): # avoid reprocessing already processed data
                        analyzed_months = analyzed_months_dict[stat]

                        frame_PIQc = pd.DataFrame() 

                        for id in more_inst_id:  # read from multiple instrument stations
                            frame_PIQc = frame_PIQc.append(read_L1_ICOS_PIQc(station=stat, height=h, specie=spec, inst_ID=id))
                        frame_PIQc.sort_values(by='Datetime', inplace=True)

                        for month_str in analyzed_months: # select only analyzed months
                            year  = int(month_str.split('-')[0])
                            month = int(month_str.split('-')[1])
                            month_frame = frame_PIQc[(frame_PIQc['Datetime'].dt.year == year) & 
                                                     (frame_PIQc['Datetime'].dt.month == month)]
                            if (stat=='PUI') & (year==2020) & (month==6):
                               print('reducing PUI 06/2020 days')
                               month_frame = month_frame[month_frame['Datetime'].dt.day < 15]
                            frame_PIQc_sel=frame_PIQc_sel.append(month_frame, ignore_index=True)

                        if len(frame_PIQc_sel) > 0: 
                            sel.add_spike_cols_PIQc(frame_PIQc_sel, spec)
                            frame_double_spiked = frame_spiked.merge(frame_PIQc_sel[['Datetime', 'spike_'+spec.lower()+'_PIQc']], on='Datetime', how ='inner')
                            out_filename = infile_spiked + '_PIQc'
                            frame_double_spiked.to_csv(out_filename, sep=';', index=False)
                        else:
                            print('no data found')
                    else:
                        print('data already processed')

def add_PIQc_high_spikes_column(stations, alg, param):
    """
    add the column with the "high" spikes detected by PIs. high spikes are defined according to the difference respect to the baseline
    the baseline is obtained by a running average (over 1 hour?) 

    Parameters
    ----------
    stations : list
        list of string containing the stations names in upper case.
    alg: str
        spike algorithm name ('SD' or 'REBS')
    param: str
        value of the algorithm param. 
    Returns
    -------
    None.
    """
    config = ConfigParser()
    for stat in stations:
        config.read('stations.ini')
        heights = config.get(stat, 'height' ).split(',')
        species = config.get(stat, 'species').split(',')
        ID      = config.get(stat, 'inst_ID').split(',')
        stat=stat[0:3] # used to read also ini file with KIT_CO that is used to read CO data at KIT. In fact CO data use different instruments and a different station has to be defined in the ini file
        for inst_id in ID:
            more_inst_id = inst_id.split('+') # used to read one datafile for each instrument and provide a single output file            
            for h in heights:
                for spec in species: 
                    print(stat, inst_id, alg, param, spec, h)
                    #for id in more_inst_id:
                    infile_spiked = './data-minute-spiked/' + stat +'/' + get_L1_file_name(stat, h, spec, inst_id)+'_'+ alg +'_'+ param + '_spiked_PIQc'
                    frame_spiked = pd.read_csv(infile_spiked, sep=';')
                    frame_spiked['Datetime'] = pd.to_datetime(frame_spiked['Datetime'])
                    frame_spiked = frame_spiked.set_index('Datetime')
                    frame_spiked.insert(len(frame_spiked.columns),spec.lower()+'_rolling_mean', round(frame_spiked[spec.lower()].rolling('1H', center=True).mean(),3) )
                    frame_spiked.insert(len(frame_spiked.columns),'spike_amplitude_'+spec.lower()+'_PIQc', np.nan)
                    frame_spiked['spike_amplitude_'+spec.lower()+'_PIQc'] = frame_spiked[spec.lower()] - frame_spiked[spec.lower()+'_rolling_mean']
                    frame_spiked.loc[ frame_spiked['spike_'+spec.lower()+'_PIQc']==False, 'spike_amplitude_'+spec.lower()+'_PIQc'] = 0

                    frame_spiked.to_csv(infile_spiked+'_mean',sep=';')

def check_id_height(df, id, height):
    
    print('checking')
    df=df[['Datetime','SamplingAltitude','InstrumentIds']]
    for line in df.iterrows():
        if str(line[1])!=str(height):
            print(line[0], 'height error')
        if str(line[2])!=str(id):
            print(line[0], 'ID error')   
    print('end check')
        
def insert_datetime_col(df, pos,Y,M,D,h,m):
    """ 
    Insert a datetime column in a dataframe and removes the old year, month, day, hour and min columns 
    
    Parameters
    ---------
    df: DataFrame
        input dataframe
    pos: int
        position where to insert the DateTime column
    Y,M,D,h,m: int
        names of the Year, Month, Day, hour and minutes columns
    
    Returns
    ---------
    """
    df.insert(pos, 'Datetime', pd.to_datetime(df[[Y,M,D,h,m]]) )
    del(df[Y], df[M], df[D], df[h], df[m] )

def format_file_plot_names(stat, specie, id):
    """
    format strings for output files and plot

    Parameters
    ----------
    stat, specie, id : str
        details from the ini file

    Returns
    -------
    hist_pathname : str
        plot path+title string 

    """

    plot_dir = './res_plot/'+stat+'/'
    hist_filesuff = stat+'_'+specie+'_'+id+'.pdf'
    hist_titlenm = specie+' stdev at '+stat+' '+id
    
    
    return plot_dir, hist_filesuff, hist_titlenm

def read_events(stat):
    """
    read events from ini file and return a list of datetime where are reported the start and end date of each event 
    Parameters
    ----------
    stat : str
        station name in upper case
    Returns
    -------
    events : 2D list of Datetime objects
        list that contains the start and end date of each event.
    """
    config =ConfigParser()
    config.read('stations.ini')
    ev_list = config.get(stat, 'events' ).split(',')
    events = []
    for ev in ev_list:
        evv = ev.split(' ')
        print(evv)
        evv[0] = dt.datetime.strptime(evv[0] ,'%d/%m/%Y') #convert to datetime object
        evv[1] = dt.datetime.strptime(evv[1] ,'%d/%m/%Y')
        events.append(evv)        
    return events



























