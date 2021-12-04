#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 17:11:17 2021

@author: Cosimo Fratticioli
@contact: c.fratticioli@isac.cnr.it
"""

import spikes_formatting_functions as fmt
import spikes_plot as splt
import pandas as pd
from configparser import ConfigParser
import datetime as dt
import spikes_data_selection_functions as sel

stations = ['IPR', 'SAC', 'CMN', 'KIT_CO', 'KIT', 'JUS', 'JFJ','PUI','UTO']
#stations = ['IPR', 'SAC', 'CMN']
years = [2019,2020]
config=ConfigParser()
algorithms = [['SD', '0.1', '0.5', '1.0', '1.5', '2.0', '2.5', '3.0', '3.5', '4.0'], 
               ['REBS', '1', '2', '3', '4', '5', '6', '7', '8', '9']]
#algorithms = [['REBS', '1', '2', '3', '4', '5', '6', '7', '8', '9']]
# used to plot custom events without modify the config file
custom_events=[]
#custom_events = [[ dt.datetime.strptime('2019-1-1' ,'%Y-%m-%d'),dt.datetime.strptime('2019-12-31' ,'%Y-%m-%d')]]
                  # [dt.datetime.strptime('2020-1-1','%Y-%m-%d'),dt.datetime.strptime('2020-12-31','%Y-%m-%d')]]
#algorithms = [['SD', '0.1','0.5','1.0', '1.5', '2.0', '2.5', '3.0', '3.5', '4.0']]

#### #### #### #### #### #### #### #### #### #### #### #### ####
####  elaborate minute data and write them to smaller files ####
# N.B. this function has to be executed only once

#for algo in algorithms:
#    alg = algo[0]
#    for param in algo [1:len(algo)]:
#        print(alg, param)
#        fmt.write_spiked_file(stations, alg, param)
# ### #### #### #### #### #### #### #### #### #### #### #### ####


 for stat in stations:
     config.read('stations.ini') 
     heights = config.get(stat, 'height' ).split(',')
     species = config.get(stat, 'species').split(',')
     ID      = config.get(stat, 'inst_ID').split(',')
     stat = stat[0:3] # check used to read also ini file with KIT_CO that is used to read CO data at KIT. In fact CO data use different instruments and a different station has to be defined in the ini file
     if custom_events != []:
         events=custom_events
     else:
         events  = fmt.read_events(stat)
     print('\nSTATION:', stat)
     for id in ID:
         for algo in algorithms:
             alg = algo[0] # read current algorithm name (REBS or SD)
            # for param in algo [1:len(algo)]: # loop over parameter values
            #     print('\nplot for ', alg, param)
            #     for spec in species:
            #         inst_frame = [] # list of dataframe with instrument data
                    
            #         for h in heights:
            #             in_filename = './data-minute-spiked/' + stat +'/' + fmt.get_L1_file_name(stat, h, spec, id) +'_'+alg+'_'+param+ '_spiked'
            #             inst_frame.append( pd.read_csv(in_filename, sep=';', parse_dates=['Datetime'] ) ) # read dataframe with spiked data

                    # #### ####plot histograms ####
                    #splt.plot_sd_histo(inst_frame, stat, id, alg, param, spec, heights)

                    # #### #### Q-Qplot #### ####
                    # print('processing qqplot')
                    # splt.plot_sd_qqplot(inst_frame, stat, id, alg, param, spec, heights)

                    ## #### plot events timeseries #### ####
                    # for ev in events:
                    #     print('processing event', ev[0])
                    #     #splt.plot_sd_event(inst_frame, stat, id, alg, param, spec, heights, ev)
                    #     #splt.plot_conc_sd_event(inst_frame, stat, id, alg, param, spec, heights, ev)
                    #     splt.plot_conc_event(inst_frame, stat, id, alg, param, spec, heights, ev)
                    #     #splt.plot_conc_sd_event_histo(inst_frame, stat, id, alg, param, spec, heights, ev)

                    # #### #### plot monthy timeseries #### ####
                    # for year in years:
                    #     for mth in range(1,13):
                    #             splt.plot_sd_time([sel.select_month( inst_frame[i], year, mth ) for i in range(len(heights))], 
                    #                               stat=stat, 
                    #                               spec=spec, 
                    #                               id=id, 
                    #                               heights=heights)

         #### #### plot seasonal cycle #### #### 
         for spec in species:
             inst_frame = [] # list of dataframe with instrument data
             for h in heights:
                     print('plot season and daily cycle', id, spec, h)
                     splt.plot_season(stat, id, algorithms, spec, h, years)
                     splt.plot_season_daily_cycle(stat, id, algorithms, spec, h )

#### #### heatmap #### ###
for spec in ['CO2','CH4','CO']:
    for algo in algorithms:
        sel.write_heatmap_table(stations, years, algo, spec)

coupled_algo = [(algorithms[0][i], algorithms[1][i]) for i in range(min(len(algorithms[0]),len(algorithms[1])))]
#for algos in coupled_algo[1:len(coupled_algo)]:
for algos in coupled_algo[1:3]:
    splt.plot_heatmap_monthly_diff(coupled_algo[0], algos)











