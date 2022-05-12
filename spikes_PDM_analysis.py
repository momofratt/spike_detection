#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 21 16:56:09 2022

@author: cosimo
"""
import pandas as pd
import matplotlib.pyplot as plt
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import numpy as np
import spikes_formatting_functions as fmt
import spikes_data_selection_functions as sel
import spikes_statistics as stats
from configparser import ConfigParser

frame_tdf = pd.read_csv('./data-minute/PDM-minute-data/pdm_ete_2015/tdf_ch4_all_synchro.txt', sep=' ')
frame_tdf.insert(4,'GET_corr', (frame_tdf['GET']-9.)/1.015) 
frame_tdf.insert(0,'Datetime', pd.to_datetime(frame_tdf['DATE']+' '+frame_tdf['TIME'], format='%Y-%m-%d %H:%M:%S'))
frame_tdf.set_index('Datetime')

# rimuove fluttuazioni troppo elevate:
frame_tdf.insert(3,'ICOS_1h_stdev', frame_tdf['ICOS'].rolling(window=30, center=True).std())
frame_tdf.insert(5,'GET_corr_diff', frame_tdf['GET_corr'].diff())
frame_tdf.loc[np.abs(frame_tdf['GET_corr_diff'])>15,'GET_corr']=np.nan

config=ConfigParser()
config.read('stations.ini') 
heights = config.get('PDM', 'height' ).split(',')
species = config.get('PDM', 'species').split(',')
ID      = config.get('PDM', 'inst_ID').split(',')
events  = fmt.read_events('PDM')

algorithms = [['SD', '1.0'],  ['REBS', '3','5']]
fig, ax = plt.subplots(1,3,figsize=(15,5))
i = 0
for algo in algorithms:
    for param in algo[1:len(algo)+1]:
        spike_frame = fmt.read_spike_file(algo[0], param, 'PDM', '10.0', '222')
        spike_frame=spike_frame[(spike_frame['Datetime']>events[0][0]) & (spike_frame['Datetime']<events[0][1])] 
        sel.add_spike_cols(spike_frame, ['ch4'])

        out_frame = pd.DataFrame()
        out_frame.insert(0,'Datetime', frame_tdf['Datetime'])
        out_frame.insert(1,'ch4',frame_tdf['ICOS'])
        out_frame.insert(2,'Stdev',np.nan)
        out_frame.insert(3,'InstrumentId',ID[0])

        out_frame = out_frame.merge(spike_frame[['Datetime','spike_ch4']], how = 'left', on='Datetime') # add spike column with True values corresponding to spikes
        out_frame['spike_ch4'] = out_frame['spike_ch4'].fillna('False')
        out_frame.insert(5,'spike_ch4_PIQc',False)
        out_frame = out_frame.merge(frame_tdf[['Datetime','GET_corr']], how = 'left',  on='Datetime' ) # add spike column with True values corresponding to spikes
        out_frame.insert(5,'ch4_diff',np.abs(out_frame['ch4']-out_frame['GET_corr']))

        out_frame.loc[out_frame['ch4_diff']>6, 'spike_ch4_PIQc']=True
        del out_frame['ch4_diff'], out_frame['GET_corr']
        infile_spiked = './data-minute-spiked/PDM/' + fmt.get_L1_file_name('PDM', heights[0], 'CH4', ID[0])+'_'+ algo[0] +'_'+ param + '_spiked' # write "spiked" dataframe on file
        out_filename = infile_spiked + '_PIQc'

        out_frame.to_csv(out_filename,sep=';')
        fmt.add_PIQc_high_spikes_column(['PDM'], algo[0], param)
        spiked_frame = pd.read_csv(out_filename+'_mean', sep=';')
        spiked_frame = stats.add_high_spikes_col(spiked_frame, 'ch4', 'single', '') # add high spikes column
        spiked_frame['Datetime']=pd.to_datetime(spiked_frame['Datetime'])
        frame = frame_tdf[['Datetime','ICOS','GET_corr']]
        frame = frame.merge(spiked_frame[['Datetime','spike_ch4','spike_ch4_PIQc','high_spike_ch4_PIQc']], on='Datetime', how='left')
        ax[i].scatter( frame['ICOS'], frame['GET_corr'], c='black', s=2, label = 'all data')
        # ax[i].scatter( frame[frame['spike_ch4_PIQc']]['ICOS'], frame[frame['spike_ch4_PIQc']]['GET_corr'], c='orange', s=2)
        ax[i].scatter( frame[frame['spike_ch4']==False]['ICOS'], frame[ frame['spike_ch4']==False]['GET_corr'], c='orange', s=2, label = 'despiked data')
        # ax[i].scatter( frame[frame['spike_ch4']==True]['ICOS'], frame[ frame['spike_ch4']==True]['GET_corr'], c='red', s=2)
        
        #ax[i].scatter(spiked_frame['ch4'], spiked_frame[spiked_frame['spike_ch4_PIQc']==True]['ch4'])
        ax[i].grid()
        ax[i].set_xlim(1800,2200)
        ax[i].set_ylim(1800,2200)
        ax[i].plot(np.arange(1800,2300,50),np.arange(1800,2300,50), ls='--', c='chartreuse' )
        ax[i].set_title(str(algo[0])+' '+str(param))
        # ax[i].set_aspect('equal')
        i=i+1
ax[2].legend()
plt.savefig('scatter_el_yazidi.png', dpi=300)
plt.show()
# PLOT

#fig = make_subplots(rows=1, cols=1)
#fig.add_trace( go.Scatter(x=frame_tdf.index, y=frame_tdf['ICOS'], mode = "lines",  line = {'color' : 'red'}, name = 'ICOS'), row=1, col=1)
#fig.add_trace( go.Scatter(x=frame_tdf.index, y=frame_tdf['GET_corr'], mode = "lines",  line = {'color' : 'cornflowerblue'}, name = 'GET'), row=1, col=1)

#fig.add_trace( go.Scatter(x=frame_tdf.index, y=frame_tdf['GET_corr']+4, mode = "lines",  line = {'color' : 'cornflowerblue','width':0.5}, name = 'GET'), row=1, col=1)
#fig.add_trace( go.Scatter(x=frame_tdf.index, y=frame_tdf['GET_corr']-4, mode = "lines",  line = {'color' : 'cornflowerblue','width':0.5}, name = 'GET'), row=1, col=1)
##fig.add_trace( go.Scatter(x=frame_tdf.index, y=frame_tdf['GET_corr']+frame_tdf['ICOS_1h_stdev'], mode = "lines",  line = {'color' : 'cornflowerblue','width':0.5}, name = 'GET'), row=1, col=1)
##fig.add_trace( go.Scatter(x=frame_tdf.index, y=frame_tdf['GET_corr']-frame_tdf['ICOS_1h_stdev'], mode = "lines",  line = {'color' : 'cornflowerblue','width':0.5}, name = 'GET'), row=1, col=1)

#fig.write_html('prova_PDM.html')

