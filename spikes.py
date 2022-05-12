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
import spikes_statistics as stats
#stations = ['SAC', 'CMN', 'IPR', 'KIT_CO', 'KIT', 'JUS', 'JFJ','PUI','UTO']
# stations=['CMN','UTO','IPR','JUS','PUI']
#stations = ['CMN','JFJ','UTO','IPR','JUS','KIT','PUI','SAC_329','SAC']
#stations = ['JFJ']
# stations = ['SAC_329']
# stations = ['SAC_329']
# stations = ['IPR','SAC','KIT']

years = [2019,2020]
config=ConfigParser()
#algorithms = [['SD', '0.1', '0.5', '1.0', '1.5', '2.0', '2.5', '3.0', '3.5', '4.0'],
#                ['REBS', '1', '2', '3', '4', '5', '6', '7', '8', '9','10']]
# algorithms = [['REBS', '10']]
stations = ['PDM']
algorithms = [['SD', '1.0'],  ['REBS', '3','5']]
# algorithms = [['SD', '0.1']]
# algorithms = [['SD', '0.1', '0.5', '1.0', '1.5', '2.0']]

# used to plot custom events without modify the config file
custom_events=[]
#custom_events = [[ dt.datetime.strptime('2020-1-1' ,'%Y-%m-%d'),dt.datetime.strptime('2020-2-1' ,'%Y-%m-%d')]]
                  # [dt.datetime.strptime('2020-1-1','%Y-%m-%d'),dt.datetime.strptime('2020-12-31','%Y-%m-%d')]]
#algorithms = [['SD', '0.1','0.5','1.0', '1.5', '2.0', '2.5', '3.0', '3.5', '4.0']]

#### #### #### #### #### #### #### #### #### #### #### #### ####
####  elaborate minute data and write them to smaller files ####
# N.B. this function has to be executed only once

# for algo in algorithms:
#     alg = algo[0]
#     for param in algo [1:len(algo)]:
#         print(alg, param)
#         fmt.write_spiked_file(stations, alg, param)

# ### #### #### #### #### #### #### #### #### #### #### #### ####

#### #### #### #### #### #### #### #### #### #### #### #### ####
####  add column with PIs manual flags to the spiked data   ####
# N.B. this function has to be executed only once

# for algo in algorithms:
#   alg = algo[0]
#   for param in algo [1:len(algo)]:
#       print(alg, param)
#       fmt.add_PIQc_column(stations,alg,param)
#       fmt.add_PIQc_high_spikes_column(stations, alg, param)

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
#         for algo in algorithms:
#             alg = algo[0] # read current algorithm name (REBS or SD)
#             for param in algo [1:len(algo)]: # loop over parameter values
#                 print('\nplot for ', alg, param)
#                 for spec in species:
#                     inst_frame = [] # list of dataframe with instrument data
#                     # inst_frame_PIQc = [] # list of dataframe with instrument data after PIQc
#                     for h in heights:
#                         in_filename = './data-minute-spiked/' + stat +'/' + fmt.get_L1_file_name(stat, h, spec, id) +'_'+alg+'_'+param+ '_spiked'
#                         inst_frame.append( pd.read_csv(in_filename, sep=';', parse_dates=['Datetime'] ) ) # read dataframe with spiked data
#             #             inst_frame_PIQc.append( pd.read_csv(in_filename+'_PIQc', sep=';', parse_dates=['Datetime'] ) ) # read dataframe with spiked data after PIQc
#                     #### ####plot histograms ####
#                     #splt.plot_sd_histo(inst_frame, stat, id, alg, param, spec, heights)

#                     #### #### Q-Qplot #### ####
#                     #print('processing qqplot')
#                     #splt.plot_sd_qqplot(inst_frame, stat, id, alg, param, spec, heights)

#                     # #### plot events timeseries #### ####
                    #for ev in events:
                        #print('processing event', ev[0])
                        ## splt.plot_sd_event(inst_frame, stat, id, alg, param, spec, heights, ev)
                        ## splt.plot_conc_sd_event(inst_frame, stat, id, alg, param, spec, heights, ev)
                        #splt.plot_conc_event(inst_frame, stat, id, alg, param, spec, heights, ev)
#                         # splt.plot_conc_sd_event_histo(inst_frame, stat, id, alg, param, spec, heights, ev)
#                     #### #### plot monthy timeseries #### ####
#                     # for year in years:
#                     #     for mth in range(1,13):
#                     #             splt.plot_sd_time([sel.select_month( inst_frame[i], year, mth ) for i in range(len(heights))], 
#                     #                               stat=stat, 
#                     #                               spec=spec, 
#                     #                               id=id, 
#                     #                               heights=heights)

        #### plot seasonal cycle #### #### 
        # for spec in species:
        #     for h in heights:
        #         print('plot season and daily cycle', id, spec, h)
        #         splt.plot_season(stat, id, algorithms, spec, h, years, log=True)
        #         splt.plot_season_daily_cycle_compact(stat, id, algorithms, spec, h, log=True)

        ### #### manual flag analysis #### #### 
        for spec in species:
            for h in heights:
                #print('\n\n******** manual flag analysis high spikes ***********', id, spec, h)
                #stats.plot_BFOR_parameters(stat, id, algorithms, spec, h, high_spikes=True, high_spikes_mode='single',quant=None)
                print('\n\n******** manual flag analysis all spikes ***********', id, spec, h)
                stats.plot_BFOR_parameters_sdrebs(stat, id, algorithms, spec, h, high_spikes=False, high_spikes_mode='single',quant=None)
                stats.plot_BFOR_parameters_sdrebs(stat, id, algorithms, spec, h, high_spikes=True, high_spikes_mode='single',quant=None)
                stats.plot_BFOR_parameters_lowhigh(stat, id, algorithms, spec, h, high_spikes_mode='single',quant=None)
        

# stats.BFOR_table(stations, algorithms, high_spikes=False, high_spikes_mode='single', quant=None)


#### boxplot of monthly differences #####
#for spec in ['CH4','CO2','CO']:
#    max_heights=[]
#    IDs = []
#    algorithms = [['SD', '0.1', '1.0', '4.0'],
#                    ['REBS', '1', '3','10']]
#    if spec == 'CO':
#        ## ATTENZIONE!!! se vuoi analizzare CO rimuovi 'KIT_CO' dalla lista di stazioni!!
#        stations = list(map(lambda x: x.replace('KIT', 'KIT_CO'), stations)) # replace KIT with KIT_CO
#        stations.remove('PUI')
#        algorithms = [['SD', '0.1', '3.0', '4.0'],
#                        ['REBS', '1', '8','10']]
#    for stat in stations:
#        config.read('stations.ini') 
#        heights = config.get(stat, 'height' ).split(',')
#        IDs.append(config.get(stat, 'inst_ID' ))
#    print('\n',spec)
#    splt.plot_season_boxplot_plotly(stations, IDs, algorithms, spec, years, False)
    #splt.plot_season_boxplot_plotly(stations, IDs, algorithms, spec, max_heights, years, True)
    #splt.plot_season_boxplot(stations, IDs, algorithms, spec, max_heights, years, '')

################################################
# plot events after manual PIQc
################################################àà
#for stat in stations:
#    config.read('stations.ini') 
#    heights = config.get(stat, 'height' ).split(',')
#    species = config.get(stat, 'species').split(',')
#    ID      = config.get(stat, 'inst_ID').split(',')
#    stat = stat[0:3] # check used to read also ini file with KIT_CO that is used to read CO data at KIT. In fact CO data use different instruments and a different station has to be defined in the ini file
#    if custom_events != []:
#        events=custom_events
#    else:
#        events  = fmt.read_events(stat)
#    print('\nSTATION:', stat)
#    for id in ID:
#        alg = algorithms[0][0] # read current algorithm name (REBS or SD)
#        param = algorithms[0][1]
#        for spec in species:
#            inst_frame_PIQc = [] # list of dataframe with instrument data after PIQc
#            for h in heights:
#                in_filename = './data-minute-spiked/' + stat +'/' + fmt.get_L1_file_name(stat, h, spec, id) +'_'+alg+'_'+param+ '_spiked_PIQc_mean'
#                inst_frame_PIQc.append( pd.read_csv(in_filename, sep=';', parse_dates=['Datetime'] ) ) # read dataframe with spiked data after PIQc
#            # #### plot events timeseries #### ####
#            for ev in events:
#                print('processing event', ev[0])
#                splt.plot_conc_event_PIQc_plotly(inst_frame_PIQc, stat, id, alg, param, spec, heights, ev, mode='single',quant=0.)
################################################
################################################


#### #### heatmap #### ###
#species = ['CO2', 'CH4', 'CO']
#for spec in species:
#    for algo in algorithms:
#        print('heatmap for', spec, algo[0])
#        sel.write_heatmap_table(stations, years, algo, spec)

#coupled_algo = [(algorithms[0][i], algorithms[1][i]) for i in range(min(len(algorithms[0]),len(algorithms[1])))]
#for algos in coupled_algo[1:len(coupled_algo)]:
#    print('plot heatmap for', coupled_algo[0])
#    splt.plot_heatmap_monthly_diff(coupled_algo[0], algos, species)











