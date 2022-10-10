# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 12:02:42 2021

@author: Cosimo Fratticioli
@contact: c.fratticioli@isac.cnr.it
"""
import matplotlib.pyplot as plt 
import matplotlib.ticker as mtick
import matplotlib.patches as mpatches
import matplotlib

import spikes_formatting_functions as fmt
import spikes_data_selection_functions as sel
import spikes_statistics as stats
import numpy as np 
from scipy.stats import scoreatpercentile
import seaborn as sea
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from spikes_statistics import min_ampl_dict
from configparser import ConfigParser
import plotly.graph_objects as go

monthly_range_CO_dict  = {'SAC':[90,240], 'CMN':[90,150], 'IPR':[120,470], 'KIT':[100,300], 'JUS':[90,350], 'JFJ':[90,150],'PUI':[],'UTO':[80,170]}
monthly_range_CO2_dict = {'SAC':[405,440], 'CMN':[400,425], 'IPR':[405,480], 'KIT':[405,480], 'JUS':[410,460], 'JFJ':[400,425],'PUI':[390,430],'UTO':[400,425]}
monthly_range_CH4_dict = {'SAC':[1950,2050], 'CMN':[1900,2000], 'IPR':[1975,2150], 'KIT':[1950,2150], 'JUS':[1950,2100], 'JFJ':[1900,1975],'PUI':[1925,2030],'UTO':[1925,2025]}
daily_range_CO2_dict = {'SAC':[410,430], 'CMN':[400,425], 'IPR':[410,450], 'KIT':[410,440], 'JUS':[400,450], 'JFJ':[400,420],'PUI':[400,430],'UTO':[400,430]}
daily_range_CH4_dict = {'SAC':[1950,2050], 'CMN':[1930,1980], 'IPR':[1975,2150], 'KIT':[1950,2075], 'JUS':[1950,2100], 'JFJ':[1920,1955],'PUI':[1920,2010],'UTO':[1955,2010]}
daily_range_CO_dict  = {'SAC':[90,180], 'CMN':[90,150], 'IPR':[100,400], 'KIT':[125,200], 'JUS':[90,260], 'JFJ':[100,130],'PUI':[],'UTO':[85,145]}


def get_indexes_for_monthly_boxplot(alg, params, stat='', spec=''):
    """ get index for a given algorithm and parameter"""
    
    all_algorithms = [['SD', '0.1', '0.5', '1.0', '1.5', '2.0', '2.5', '3.0', '3.5', '4.0'],
                      ['REBS', '1', '2', '3', '4', '5', '6', '7','8' , '9', '10']]
    
    if stat[0:3] in ['ZSF', 'SAC','KIT','JFJ']:
        if spec in ['CO2','CH4']:
            all_algorithms = [['SD', '0.1', '1.0', '4.0'],
                              ['REBS', '1', '3', '10']]
        else:
             all_algorithms = [['SD', '0.1', '3.0', '4.0'],
                               ['REBS', '1', '8', '10']]   
    indexes=[]
    for algo in all_algorithms:
        if algo[0]!=alg:
            pass
        else:
            all_params = algo[1:]
            for par in params:
                i = 0
                for all_par in all_params:
                    if par==all_par:
                        indexes.append(i)
                    i+=1
    print('indexes',alg, indexes)
    return indexes

def plot_season_daily_cycle(stat, id, algorithms, spec, height, log):
    """
    plot average daily time series. 
    Parameters
    ----------
    data, spike_data: list of Dataframes
        data to be plotted. If len(data)>1 then more histograms are plotted.
    stat, spec, id: str
        details for station name, instrument id, chemical specie from the ini file
    algorithms: list of str
        algorithms array defined in spikes.py
    height: str
         sampling height
    log: bool
         set log scale on delta plots
    Returns
    -------
    None.

    """
    def plot_daily_cycle(season_data, season_data_diff, ax, alg, params):
        non_spiked=np.array(season_data[-1])
        min, max = 0, 0
        for j in range(len(season_data)-1):
            delta = -non_spiked+np.array(season_data[j])
            #ax[0].plot(delta, label = alg +' '+params[j])
            ax[0].plot(season_data_diff[j], label = alg +' '+params[j])
            ax[1].plot(np.array(season_data[j]), label = alg +' '+params[j])
            minim, maxim = np.min(delta), np.max(delta)
            if (minim < min):
                min = minim
            if (maxim>max):
                max=maxim

        if log:
            if (spec == 'CO') |( spec =='CH4'):
                mticks = [ 9,  8,  7,  6,  5,  4,  3,  2,-2,-3,-4,-5,-6,-7,-8,-9,-20,-30,-40,-50,-60,-70,-80,-90 ]
                Mticks = [10, 1,  0, -1, -10, -100]
                ax[0].axhline(-2, ls='--', c='r')
                ax[0].axhline(2, ls='--', c='r')
                linthresh=1
                min = -100
                max = 10

            else:
                mticks = [ 9,  8,  7,  6,  5,  4,  3,  2, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, -0.2, -0.4, -0.5, -0.6, -0.7, -0.8 ,-0.9, -2,-3,-4,-5,-6,-7,-8,-9 ]
                Mticks = [10, 1,  0.1, 0, -0.1, -1, -10]
                ax[0].axhline(-0.1, ls = '--', c='r')
                ax[0].axhline(0.1, ls = '--', c='r')
                linthresh=0.1
                min = -10
                max = 10


            ax[0].set_yscale('symlog',linthresh=linthresh)
            ax[0].set_yticks(Mticks)
            ax[0].set_yticks(mticks, minor=True)

            if max <0.1:
                max = 0.1
            ax[0].set_ylim(bottom = min*1.15)
            ax[0].set_ylim(top = max*1.15)

            ax[0].set_ylim(bottom = min*1.05)
            ax[0].set_ylim(top = max*1.05)
            # if spec == 'CO':
            #     yrange = daily_range_CO_dict[stat]
            #     ax[1].set_ylim(yrange[0], yrange[1])
            # if spec == 'CO2':
            #     yrange = daily_range_CO2_dict[stat]
            #     ax[1].set_ylim(yrange[0], yrange[1])
            # if spec == 'CH4':
            #     yrange = daily_range_CH4_dict[stat]
            #     ax[1].set_ylim(yrange[0], yrange[1])


        ax[1].plot(non_spiked, label = 'non-spiked', c='black',ls='--')
        ax[0].set_ylabel('Concentration difference '+fmt.get_meas_unit(spec))
        ax[1].set_ylabel('Concentration '+fmt.get_meas_unit(spec))
        ax[1].legend(bbox_to_anchor=(1,1), loc="upper left")
        for a in ax:
            a.grid(which = 'major')
            a.set_xticks(np.arange(0,24,2))
        ax[0].grid(b=True, which='minor', linestyle='-', alpha=0.2)
    # array with season name (for filename and title name), months(used for data selection) and relative year (used in title name)
    log_folder=''
    log_suff  =''
    seasons = [('DJF',[12,3], ' 2019-2020'),('MAM',[3,6], ' 2020'),('JJA',[6,9], ' 2020'),('SON',[9,12], ' 2020') ]
    for season in seasons:
        print(season[0])
        fig, ax = plt.subplots(2,2, figsize=(12,8))
        for i in range(len(algorithms)):
            alg = algorithms[i][0] # read current algorithm name (REBS or SD)
            params = algorithms[i][1:len(algorithms[i])] # get list of parameters
            season_day_data, season_day_data_diff = sel.get_daily_season_data(stat, id, alg, params, spec, height,season[1],season[0])
            plot_daily_cycle(season_day_data, season_day_data_diff, ax[i], alg, params)
        if log:
            log_folder = 'log/'
            log_suff='_logscale'

        fig.suptitle("Daily mean cycle of concentration: absolute values and difference between non-spiked and spiked data\n"+spec+' at '+stat+' '+id+'   height=' + height + ' m   season='+season[0]+season[2])
        plt.savefig('./res_plot/'+stat+'/daily_cycle/'+log_folder+'seasonal_daily_cycle_'+season[0]+'_'+stat+'_'+spec+'_'+id+'_h'+height+log_suff+'.png', format='png', bbox_inches="tight")
        plt.close(fig)

def plot_season_daily_cycle_compact(stat, id, algorithms, spec, height, log, years=[2019,2020]):
    """    more compact plot respect to plot_season_daily_cycle(function)    """
    colors =[['#DDA0DD','#FF1493','#8A2BE2' ],
             ['skyblue', 'deepskyblue','steelblue']]

    def plot_daily_cycle(season_data, season_data_diff, non_spiked, ax_diff, ax_abs,  alg, params, indexes):
        min, max = 0, 0
        if alg =='SD':
            offset_index=0
        else:
            offset_index=1
        for j in range(len(season_data)):
            #ax[0].plot(delta, label = alg +' '+params[j])
            ax_diff.plot(season_data_diff[j], label = alg +' '+params[indexes[j]], c=colors[offset_index][j]) # plot differences
            ax_abs.plot(np.array(season_data[j]), label = alg +' '+params[indexes[j]], c=colors[offset_index][j])

        if log:
            if (spec == 'CO') |( spec =='CH4'):
                mticks = [ 9,  8,  7,  6,  5,  4,  3,  2,-2,-3,-4,-5,-6,-7,-8,-9,-20,-30,-40,-50,-60,-70,-80,-90 ]
                Mticks = [10, 1,  0, -1, -10, -100]
                ax_diff.axhline(-2, ls='--', c='r')
                ax_diff.axhline(2, ls='--', c='r')
                linthresh=1
                wmo_thresh=2
                min = -100
                max = 1

            else:
                mticks = [ 9,  8,  7,  6,  5,  4,  3,  2, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, -0.2, -0.4, -0.5, -0.6, -0.7, -0.8 ,-0.9, -2,-3,-4,-5,-6,-7,-8,-9 ]
                Mticks = [10, 1,  0.1, 0, -0.1, -1, -10]
                ax_diff.axhline(-0.1, ls = '--', c='r')
                ax_diff.axhline(0.1, ls = '--', c='r')
                linthresh=0.1
                wmo_thresh = 0.1
                min = -10
                max = 0.1


            ax_diff.set_yscale('symlog',linthresh=linthresh)
            ax_diff.set_yticks(Mticks)
            ax_diff.set_yticks(mticks, minor=True)

            if max <0.1:
                max = 0.1
            ax_diff.set_ylim(bottom = min*1.15)
            ax_diff.set_ylim(top = max*1.15)

            ax_diff.set_ylim(bottom = min*1.05)
            ax_diff.set_ylim(top = max*1.05)
            # if spec == 'CO':
            #     yrange = daily_range_CO_dict[stat]
            #     ax[1].set_ylim(yrange[0], yrange[1])
            # if spec == 'CO2':
            #     yrange = daily_range_CO2_dict[stat]
            #     ax[1].set_ylim(yrange[0], yrange[1])
            # if spec == 'CH4':
            #     yrange = daily_range_CH4_dict[stat]
            #     ax[1].set_ylim(yrange[0], yrange[1])

        if alg =='REBS': # do only once the following 
            ax_abs.plot(non_spiked, label = 'non-spiked', c='black',ls='--', lw=2)
            ax_abs.fill_between(np.arange(0,24,1), non_spiked-wmo_thresh, non_spiked+wmo_thresh,color='gray', alpha=0.3)
            ax_abs.set_ylabel(spec+' '+fmt.get_meas_unit(spec))
            ax_abs.set_xticks(np.arange(0,24,2))
            ax_abs.grid(True)
            ax_abs.set_xlabel('hours')
            ax_abs.yaxis.set_label_position("right")
            ax_abs.yaxis.tick_right()
        #ax_abs.legend(bbox_to_anchor=(1.1,1), loc="upper left")
        ax_abs.legend()
        ax_diff.set_xlabel('hours')
        ax_diff.set_ylabel('Δ'+spec+' '+fmt.get_meas_unit(spec))
        ax_diff.set_xticks(np.arange(0,24,2))
        ax_diff.grid(which = 'major')
        ax_diff.grid(b=True, which='minor', linestyle='-', alpha=0.2)
        ax_diff.grid(True, which='both')
        if alg=='SD':
            ax_diff.set_xticklabels(['' for i in range(12)])

    # array with season name (for filename and title name), months(used for data selection) and relative year (used in title name)
    log_folder=''
    log_suff  =''
    seasons = [('DJF',[12,3], ' 2019-2020'),('MAM',[3,6], ' 2020'),('JJA',[6,9], ' 2020'),('SON',[9,12], ' 2020') ]
    
    for season in seasons:
        print(season[0])
        
        plt.style.use('ggplot')
        fig = plt.figure(figsize=(10,6.6))
        fig.tight_layout()
        fig.subplots_adjust(hspace=0.05, wspace=0.05)
        ax = []
        ax.append(plt.subplot2grid((2,2), (0,0)))
        ax.append(plt.subplot2grid((2,2), (1,0)))
        ax.append(plt.subplot2grid((2,2), (0,1), rowspan=2))

        for i in range(len(algorithms)):
            alg = algorithms[i][0] # read current algorithm name (REBS or SD)

            if spec == 'CO':
                if alg =='SD': # define selected parameters
                    subparams=['0.1','3.0','4.0']
                else:
                    subparams=['1','8','10']
            else:
                if alg =='SD': # define selected parameters
                    subparams=['0.1','1.0','4.0']
                else:
                    subparams=['1','3','10']

            params = algorithms[i][1:len(algorithms[i])] # get list of parameters
            season_day_data, season_day_data_diff = sel.get_daily_season_data(stat, id, alg, params, spec, height,season[1],season[0],years=years)
            non_spiked = np.array(season_day_data[-1])
            season_day_data_sub, season_day_data_diff_sub = [], [] # define sublists with selected parameters
            indexes = get_indexes_for_monthly_boxplot(alg, subparams,stat=stat,spec=spec)
            for k in indexes:
                season_day_data_sub.append(season_day_data[k])
                season_day_data_diff_sub.append(season_day_data_diff[k])
            plot_daily_cycle(season_day_data_sub, season_day_data_diff_sub, non_spiked, ax[i], ax[2], alg, params, indexes)
        if log:
            log_folder = 'log/'
            log_suff='_logscale'

        fig.suptitle("Daily mean cycle of concentration: absolute values and difference between non-spiked and spiked data\n"+spec+' at '+stat+' '+id+'   height=' + height + ' m   season='+season[0]+season[2])
        plt.savefig('./res_plot/'+stat+'/daily_cycle/'+log_folder+'seasonal_daily_cycle_compact_'+season[0]+'_'+stat+'_'+spec+'_'+id+'_h'+height+log_suff+'.png', format='png', bbox_inches="tight", dpi=300)
        plt.close(fig)


def plot_season( stat,  id, algorithms, spec, height,years, log):
    """
    plot seasonal time series. I.E. montlhy median for different algorithms and parameters
    Parameters
    ----------
    stat, spec, id: str
        details for station name, instrument id, chemical specie from the ini file
    algorithms: list of str
        algorithms array defined in spikes.py
    height: str
         sampling height
    Returns
    -------
    None.

    """

    def plot_monthly(monthly_data, monthly_data_diff, ax, alg, params):
        non_spiked=np.array(monthly_data[-1])
        min,max=0,0
        for j in range(len(monthly_data_diff)):
            # delta = np.array(monthly_data[j])-non_spiked
            delta = np.array(monthly_data_diff[j])
            ax[0].plot(delta, label = alg +' '+params[j])
            ax[1].plot(np.array(monthly_data[j]), label = alg +' '+params[j])
            minim, maxim = np.min(delta), np.max(delta)
            if (minim < min):
                min = minim
            if (maxim>max):
                max=maxim
        if log:
            if (spec == 'CO') |( spec =='CH4'):
#                mticks = [ 9,  8,  7,  6,  5,  4,  3,  2, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, -0.2, -0.4, -0.5, -0.6, -0.7, -0.8 ,-0.9,-2,-3,-4,-5,-6,-7,-8,-9,-20,-30,-40,-50,-60,-70,-80,-90 ]
                mticks = [ 9,  8,  7,  6,  5,  4,  3,  2,-2,-3,-4,-5,-6,-7,-8,-9,-20,-30,-40,-50,-60,-70,-80,-90 ]
                Mticks = [10, 1,  0, -1, -10, -100]
                ax[0].axhline(-2, ls='--', c='r')
                ax[0].axhline(2, ls='--', c='r')
                min = -100
                max = 10
                linthresh=1
            else:
                mticks = [ 9,  8,  7,  6,  5,  4,  3,  2, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, -0.2, -0.4, -0.5, -0.6, -0.7, -0.8 ,-0.9, -2,-3,-4,-5,-6,-7,-8,-9 ]
                Mticks = [10, 1,  0.1, 0, -0.1, -1, -10]
                ax[0].axhline(-0.1, ls = '--', c='r')
                ax[0].axhline(0.1, ls = '--', c='r')
                min = -10
                max = 10
                linthresh=0.1
            ax[0].set_yscale('symlog',linthresh=linthresh)
            ax[0].set_yticks(Mticks)
            ax[0].set_yticks(mticks, minor = True)


            ax[0].set_ylim(bottom = min*1.05)
            ax[0].set_ylim(top = max*1.05)
            # if spec == 'CO':
            #     yrange = monthly_range_CO_dict[stat]
            #     ax[1].set_ylim(yrange[0], yrange[1])
            # if spec == 'CO2':
            #     yrange = monthly_range_CO2_dict[stat]
            #     ax[1].set_ylim(yrange[0], yrange[1])
            # if spec == 'CH4':
            #     yrange = monthly_range_CH4_dict[stat]
            #     ax[1].set_ylim(yrange[0], yrange[1])

        ax[1].plot(non_spiked, label = 'non-spiked', c='black',ls='--')
        ax[0].set_ylabel('Δ'+spec+' '+fmt.get_meas_unit(spec))
        ax[1].set_ylabel(spec+' '+fmt.get_meas_unit(spec))
        ax[1].legend(bbox_to_anchor=(1,1), loc="upper left")

        for a in ax:
            a.grid(which='major')
            a.set_xticks(np.arange(0,int(len(years)*12-1),2))
            #months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
            #labels = ['Jan\n\'19','Mar\n\'19','May\n\'19','Jul\n\'19','Sep\n\'19','Nov\n\'19','Jan\n\'20','Mar\n\'20','May\n\'20','Jul\n\'20','Sep\n\'20','Nov\n\'20']
            labels = []
            for s in years:
                labels = labels+['Jan\n\''+str(s)[2:4], 'Mar\n\''+str(s)[2:4],'May\n\''+str(s)[2:4],'Jul\n\''+str(s)[2:4],'Sep\n\''+str(s)[2:4],'Nov\n\''+str(s)[2:4] ]

            a.set_xticklabels(labels)
        ax[0].grid(b=True, which='minor', linestyle='-', alpha=0.4)
        ax[1].grid(b=True, which='major', linestyle='-', alpha=0.4)

    log_folder=''
    log_suff  =''
    fig, ax = plt.subplots(2,2, figsize=(12,8))
    for i in range(len(algorithms)):
        alg = algorithms[i][0] # read current algorithm name (REBS or SD)
        params = algorithms[i][1:len(algorithms[i])] # get list of parameters
        monthly_data, monthly_data_diff = sel.get_monthly_data(stat, id, alg, params, spec, height,years)
        plot_monthly(monthly_data, monthly_data_diff, ax[i], alg, params)

    if log:
        log_folder = 'log/'
        log_suff='_logscale'

    fig.suptitle("Monthly mean concrentration: absolute values and difference between non-spiked and spiked data\n"+spec+' at '+stat+' '+id+'   height=' + height + ' m')
    plt.savefig('./res_plot/'+stat+'/monthly_mean/'+log_folder+'monthly_mean_'+stat+'_'+spec+'_'+id+'_h'+height+log_suff+'.pdf', format='pdf', bbox_inches="tight")
    plt.close(fig)



def plot_season_boxplot(stations, IDs, algorithms, spec, height, years, log):
    """
    plot seasonal boxplots of monthly mean differences respect to non spiked data 
    Parameters
    ----------
    stat, spec: str
        details for stations names, instrument id, chemical specie from the ini file
    algorithms: list of str
        algorithms array defined in spikes.py
    height: list
         list of heights for the different stations
    Returns
    -------
    None.

    """
    nboxplots = len(algorithms[0])-1 #number of boxplots to be plotted
    
    def adjacent_values(vals, q1, q3):
        upper_adjacent_value = q3 + (q3 - q1) * 1.5
        upper_adjacent_value = np.clip(upper_adjacent_value, q3, vals[-1])

        lower_adjacent_value = q1 - (q3 - q1) * 1.5
        lower_adjacent_value = np.clip(lower_adjacent_value, vals[0], q1)
        return lower_adjacent_value, upper_adjacent_value

        
    def plot_monthly(monthly_data_diff, ax, stat, column,alg, params, indexes):
        monthly_data_diff = np.array(monthly_data_diff)
        count_xtick = 0 # counter to center the xtick
        for i in indexes:
            width = 0.05
            inds = 1 - (0.5*nboxplots)*0.07+count_xtick*0.07+0.035 #  is used to put the xtick onli in the center of the plot
            #ax.boxplot(monthly_data_diff[i], positions = [inds],widths=[width], patch_artist=True, notch=True)
            data = monthly_data_diff[i][monthly_data_diff[i]>0.]
            if len(data) == 0:
                data=[0,0,0] # plot empy violin if no data
            
            ax.violinplot(data, positions = [inds], widths=[width]) 
            
            data= np.sort(data)
            quartile1, medians, quartile3 = np.percentile(data, [25, 50, 75])
            whiskers = np.array([ adjacent_values(data, quartile1, quartile3)])
            whiskers_min, whiskers_max = whiskers[:, 0], whiskers[:, 1]
            
            ax.scatter(inds, medians, marker='o', color='white', s=30, zorder=3)
            ax.vlines(inds, quartile1, quartile3, color='k', alpha=0.5, linestyle='-', lw=5)
            ax.vlines(inds, whiskers_min, whiskers_max, color='k', alpha=0.5, linestyle='-', lw=1)

            count_xtick+=1
       
        if log=='log':
            if (spec == 'CO') |( spec =='CH4'):
                # mticks = [ 9,  8,  7,  6,  5,  4,  3,  2, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, -0.2, -0.4, -0.5, -0.6, -0.7, -0.8 ,-0.9,-2,-3,-4,-5,-6,-7,-8,-9,-20,-30,-40,-50,-60,-70,-80,-90 ]
                mticks = [ 0.002,0.003,0.004,0.005,0.006,0.007,0.008,0.009,0.02,0.03,0.04,0.05,0.06,0.07,0.08,0.09,0.2,0.3,0.4,0.5,0.6,0.7,0.8, 0.9, 9, 8, 7, 6, 5, 4, 3, 2, 20, 30, 40, 50, 60, 70, 80, 90 ]
                Mticks = [ 0, 0.1, 1, 10, 100 ]
                #ax.axhline(-2, ls='--', c='r')
                ax.axhline(2, ls='--', c='r')
                min = 0.001
                max = 100
               
            else:
                mticks = [ 0.0002,0.0003,0.0004,0.0005,0.0006,0.0007,0.0008,0.0009,0.002,0.003,0.004,0.005,0.006,0.007,0.008,0.009, 0.02,0.03,0.04,0.05,0.06,0.07,0.08,0.09, 0.2, 0.4, 0.5, 0.6, 0.7, 0.8 ,0.9, 2, 3, 4, 5, 6, 7, 8, 9 ]
                Mticks = [ 0, 0.01, 0.1, 1, 10]
                #ax.axhline(-0.1, ls = '--', c='r')
                ax.axhline(0.1, ls = '--', c='r')
                min = 0.0001
                max = 10
            ax.set_yscale('log')
        elif log=='symlog':
            if (spec == 'CO') |( spec =='CH4'):
                # mticks = [ 9,  8,  7,  6,  5,  4,  3,  2, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, -0.2, -0.4, -0.5, -0.6, -0.7, -0.8 ,-0.9,-2,-3,-4,-5,-6,-7,-8,-9,-20,-30,-40,-50,-60,-70,-80,-90 ]
                mticks = [ 9, 8, 7, 6, 5, 4, 3, 2, 20, 30, 40, 50, 60, 70, 80, 90 ]
                mticks = mticks + [mt*-1 for mt in mticks]
                Mticks = [ -10, -1, 0, 1, 10, 100 ]
                ax.axhline(-2, ls='--', c='r')
                ax.axhline(2, ls='--', c='r')
                linthresh=1
                min = -10
                max = 100
               
            else:
                mticks = [ 0.2, 0.4, 0.5, 0.6, 0.7, 0.8 ,0.9, 2, 3, 4, 5, 6, 7, 8, 9 ]
                mticks = mticks + [mt*-1 for mt in mticks]
                Mticks = [ -1,-0.1, 0, 0.1, 1, 10]
                ax.axhline(-0.1, ls = '--', c='r')
                ax.axhline(0.1, ls = '--', c='r')
                linthresh=0.1
                min = -1
                max = 10
            ax.set_yscale('symlog', linthresh= linthresh)
        else:
            if (spec == 'CO') |( spec =='CH4'):
                # mticks = [ 9,  8,  7,  6,  5,  4,  3,  2, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, -0.2, -0.4, -0.5, -0.6, -0.7, -0.8 ,-0.9,-2,-3,-4,-5,-6,-7,-8,-9,-20,-30,-40,-50,-60,-70,-80,-90 ]
                mticks = [ 2, 3, 4, 5, 6, 7, 8, 9 ]
                Mticks = [ 0, 1, 5, 10, 20 ]
                ax.axhline(2, ls='--', c='r')
                #ax.axhline(2, ls='--', c='r')
                min = 0
                max = 10
            else:
                mticks = [ 0.2, 0.4, 0.5, 0.6, 0.7, 0.8 ,0.9  ]
                Mticks = [ 0, 0.1, 1, 2, 3]
                ax.axhline(0.1, ls = '--', c='r')
                #ax.axhline(0.1, ls = '--', c='r')
                min = 0
                max = 3
        ax.set_yticks(Mticks)
        ax.set_yticks(mticks, minor = True)
        ax.set_ylim(bottom = min)
        ax.set_ylim(top = max)
        if column>0:
            ax.set_yticklabels(['' for i in range(len(Mticks))])  
        ax.set_xticks([1])
        ax.set_xticklabels([stat[0:3]])
        
        if column<1: 
            ax.set_ylabel('Δ'+spec+' '+fmt.get_meas_unit(spec))

        ax.grid(b=True, which='minor', linestyle='-', alpha=0.2)

    fig, ax = plt.subplots(len(algorithms),len(stations), figsize=(12,8)) 
    fig.subplots_adjust(hspace=.5, wspace=0)
    for i in range(len(algorithms)):
        alg = algorithms[i][0] # read current algorithm name (REBS or SD)
        params = algorithms[i][1:len(algorithms[i])] # get list of parameters
        for j in range(len(stations)):
            indexes = get_indexes_for_monthly_boxplot(alg, params,stat=stations[j],spec=spec)
            monthly_data, monthly_data_diff = sel.get_monthly_data(stations[j], IDs[j], alg, params, spec, height[j], years)
            monthly_data_diff = np.array(monthly_data_diff)
            plot_monthly( -monthly_data_diff, ax[i][j], stations[j], j, alg, params, indexes)

    if log=='log':
        log_suff='_logscale'
    elif log=='symlog':
        log_suff='_symlogscale'
    else:
        log_suff  =''
    
    # define legends for violin plots
    pops0 = []
    pops1 = []
    for i in range(len(params)):
        pops0.append(  mpatches.Patch(color='C'+str(i), alpha=0.5, label=algorithms[0][0]+' '+algorithms[0][i+1]))
        pops1.append(  mpatches.Patch(color='C'+str(i), alpha=0.5, label=algorithms[1][0]+' '+algorithms[1][i+1]))

    ax[0][-1].legend(handles=pops0, bbox_to_anchor=(1,1), loc="upper left")   
    ax[1][-1].legend(handles=pops1, bbox_to_anchor=(1,1), loc="upper left")   
    
    fig.suptitle("Monthly mean concrentration: difference between non-spiked and spiked data\n")
    plt.savefig('./res_plot/monthly_mean_boxplots/monthly_mean_box_'+spec+log_suff+'.pdf', format='pdf', bbox_inches="tight")
    plt.close(fig)
    
    
    
def plot_season_boxplot_plotly(stations, algorithms, spec, years, log):
    """
    plot seasonal boxplots of monthly mean differences respect to non spiked data 
    Parameters
    ----------
    stat, spec: str
        details for stations names, instrument id, chemical specie from the ini file
    algorithms: list of str
        algorithms array defined in spikes.py
    Returns
    -------
    None.

    """
    config=ConfigParser()
    config.read('stations.ini')
    if (spec == 'CO') |( spec =='CH4'): # define ranges and value for the horizontal line that reports the WMO compatibility goal (2 ppb or 0.1 ppm)
        xline = 2
        if log:
            maxim = np.log10(0.001) # ranges with log10 for plotly
            minim = np.log10(30)
        else:
            maxim = 5 # ranges with log10 for plotly
            minim = -20
    else:
        xline = 0.1
        if log:
            minim = np.log10(0.0001)
            maxim = np.log10(10)
        else:
            maxim = 0.5
            minim = -3
    
    
    fig = make_subplots(rows=2, cols=1, horizontal_spacing = 0.0)
    for i in range(len(algorithms)):
            
        alg = algorithms[i][0] # read current algorithm name (REBS or SD)
        params = algorithms[i][1:len(algorithms[i])] # get list of parameters
        indexes = get_indexes_for_monthly_boxplot(alg, params) # get the indexes corresponding to the used parameters
        
        monthly_data_diff_all_stat = [] # used to "store" the monthly tables of different stations and sampling altitudes
        for stat in stations:
            heights = config.get(stat, 'height' ).split(',')
            ID      = config.get(stat, 'inst_ID')
            for height in heights:
                monthly_data, monthly_data_diff = sel.get_monthly_data(stat, ID, alg, params, spec, height, years)
                #print(monthly_data_diff)
                monthly_data_diff_all_stat.append(monthly_data_diff)
                if len(monthly_data_diff)<9:
                    print('ERRORE numero di linee inferiore al numero di parametri:', stat, height, alg)
        # set x and y arrays in for the plotly grouped boxplot
        # print(len(monthly_data_diff_all_stat),len(monthly_data_diff_all_stat[0]))
        y=[]
        print(indexes)
        
        for l in indexes:   
            x=[]
            y_line = []
            j=0
            for stat in stations: # define x and y for grouped boxplots
                print(stat)
                heights = config.get(stat, 'height' ).split(',')
                x_line = []
                for k in range(len(heights)):
                    y_line = y_line + monthly_data_diff_all_stat[j][l]
                    x_line = x_line + [ stat[0:3]+'-'+config.get(stat, 'inst_ID')+' - '+ heights[k]+' m' for a in range(len(monthly_data_diff_all_stat[j][l])) ]
                    j+=1
                x = x + x_line
            y.append(y_line)
            
        colors = [ ['goldenrod', 'gray', 'darkolivegreen',],
                  ['goldenrod', 'gray', 'darkolivegreen',]]
        # colors = [ ['#D4AA00', '#A0A0A0', '#90AE1B',],
        #            ['#D4AA00', '#A0A0A0', '#90AE1B',]]
        #y=-np.array(y)
        print(len(x),len(y[0]),len(y[1]),len(y[2]))       
        for k in range(len(params)):
            fig.add_trace(go.Box(
                y=y[k],
                x=x,
                name=alg + ' ' +params[k],
                jitter=0.3,
                pointpos=0,
                boxpoints='all', # represent all points
                marker_color = colors[i][k],
                offsetgroup = alg + ' ' +params[k],
                legendgroup=alg),                
                row=i+1,col=1)
 
        fig.add_shape(type='line',
              x0=-0.5,
              y0=xline,
              x1=len(stations)+8-.5,
              y1=xline,
              line=dict(color='#C31D1D', dash='dot'),
              row=i+1,col=1)
        
        if not log:
            fig.add_shape(type='line',
                  x0=-0.5,
                  y0=-xline,
                  x1=len(stations)+8-.5,
                  y1=-xline,
                  line=dict(color='#C31D1D', dash='dot'),
                  row=i+1,col=1)
        
        if log:
            scale='log'
            log_suff='_log'
        else:
            scale='linear'
            log_suff=''
        
        fig.update_xaxes(showticklabels=False, 
                         row=1, col=1)
        fig.update_xaxes(tickangle=-45,
                         tickfont=dict(size=20),
                         row=2, col=1)
        fig.update_yaxes(title_text='Δ'+spec+' '+fmt.get_meas_unit(spec), 
                          type=scale,
                          range=[minim, maxim],
                          row=i+1,col=1)
                         
    fig.update_layout(boxmode='group', 
                      font=dict(size=25), 
                      width=1700, height=800,
                      title_text= spec+' Concentration Difference',
                      legend_tracegroupgap = 250,
                      template = 'plotly+gridon',
                      plot_bgcolor='#ededed'
                      )
    
    fig.write_image('./res_plot/monthly_mean_boxplots/monthly_mean_box_plotly_'+spec+log_suff+'.png')

def plot_hourly_boxplot_plotly(stations, IDs, algorithms, spec, years):
    """
    plot seasonal boxplots of monthly mean differences respect to non spiked data 
    Parameters
    ----------
    stat, spec: str
        details for stations names, instrument id, chemical specie from the ini file
    algorithms: list of str
        algorithms array defined in spikes.py
    Returns
    -------
    None.

    """
    config=ConfigParser()
    config.read('stations.ini')
    if spec =='CH4':
        xline = 2
        maxim = 4 # ranges with log10 for plotly
        minim = -40
    elif spec =='CO':
        xline = 2
        maxim = 5 # ranges with log10 for plotly
        minim = -20
    else:
        xline = 0.1
        maxim = 2
        minim = -5
    
    
    fig = make_subplots(rows=2, cols=1, horizontal_spacing = 0.0)
    for i in range(len(algorithms)):
            
        alg = algorithms[i][0] # read current algorithm name (REBS or SD)
        params = algorithms[i][1:len(algorithms[i])] # get list of parameters
        indexes = get_indexes_for_monthly_boxplot(alg, params)
        
        hourly_data_diff_all_stat = [] # used to "store" the monthly tables of different stations ad sampling altitudes
        for stat in stations:
            heights = config.get(stat, 'height' ).split(',')
            ID      = config.get(stat, 'inst_ID')
            for height in heights:
                hourly_data, hourly_data_diff = sel.get_hourly_data(stat, ID, alg, params, spec, height)
                hourly_data_diff_all_stat.append(hourly_data_diff)
                if len(hourly_data_diff)<9:
                    print('ERRORE numero di linee inferiore al numero di parametri:', stat, height, alg)
        # set x and y arrays in for the plotly grouped boxplot
        # print(len(monthly_data_diff_all_stat),len(monthly_data_diff_all_stat[0]))
        y=[]
        print(indexes)

        for l in indexes:
            """
            crea liste per fare il boxplot raggruppto per stazioni.
            Due liste: y con n colonne e m=len(indexes) righe
                       x con n colonne
            x contiene i label per raggruppare i boxplot (ogni label è definito come stat-ID-height)
            y contiene una riga per ogni parametro da plottare (ad esempio 3 righe se si plottano REBS 1,3,8). 
              Per ogni riga sono riportate le medie orarie relative al parametro (es REBS 1). 
              Per ogni riga sono presenti le medie orarie di tutte le stazioni poste una di seguito all'altra.
              Ad ogni elemento della riga y è associato un label della lista x (len(x)==len(y[k]))
              es: x=['CMN-590 - 8 m', 'CMN-590 - 8 m', 'CMN-590 - 8 m', 'IPR-629 100 m', 'IPR-629 100 m']
                  y[0]=[-1.1,-2.2,-3.3,-4.4,-5.5]
                  y[1]=[-0.1,-1.2,-2.3,-3.4,-4.5]
              sia in y[0] che in y[1] le prime tre misure sono associate a 'CMN-590 - 8 m', mentre le ultime due a 'IPR-629 100 m'
            """
            x=[]
            y_line = []
            j=0
            for stat in stations: # define x and y for grouped boxplots
                print(stat)
                heights = config.get(stat, 'height' ).split(',')
                x_line = []
                for k in range(len(heights)):
                    print('j,l =', j,l)
                    print('nlines =',len(hourly_data_diff_all_stat[j]))
                    h=hourly_data_diff_all_stat[j][l]
                    ###### replace zeros with nan ######
                    h=np.array(h)
                    #h[h==0.] = np.nan
                    h=h.tolist()
                    ###### ##### ##### ##### ##### #####
                    y_line = y_line + h                    
                    x_line = x_line + [ stat[0:3]+'-'+config.get(stat, 'inst_ID')+' - '+ heights[k]+' m' for a in range(len(hourly_data_diff_all_stat[j][l])) ]
                    j+=1
                x = x + x_line
            y.append(y_line)
            
        colors = [ ['goldenrod', 'gray', 'darkolivegreen',],
                  ['goldenrod', 'gray', 'darkolivegreen',]]

        print(len(x),len(y[0]),len(y[1]),len(y[2]))       
        for k in range(len(params)):
            fig.add_trace(go.Box(
                y=y[k],
                x=x,
                name=alg + ' ' +params[k],
                jitter=0.3,
                pointpos=0,
                boxpoints=False, # represent all points
                marker_color = colors[i][k],
                offsetgroup = alg + ' ' +params[k],
                legendgroup=alg),                
                row=i+1,col=1)
       
        fig.add_shape(type='line',
              x0=-0.5,
              y0=xline,
              x1=len(stations)+8-.5,
              y1=xline,
              line=dict(color='#C31D1D', dash='dot'),
              row=i+1,col=1)
        

        fig.add_shape(type='line',
              x0=-0.5,
              y0=-xline,
              x1=len(stations)+8-.5,
              y1=-xline,
              line=dict(color='#C31D1D', dash='dot'),
              row=i+1,col=1)
        
        fig.update_xaxes(showticklabels=False, 
                         row=1, col=1)
        fig.update_xaxes(tickangle=-45,
                         tickfont=dict(size=20),
                         row=2, col=1)
        fig.update_yaxes(title_text='Δ'+spec+' '+fmt.get_meas_unit(spec), 
                          range=[minim, maxim],
                          row=i+1,col=1)
                         
    fig.update_layout(boxmode='group', 
                      font=dict(size=25), 
                      width=1700, height=800,
                      title_text= spec+' Concentration Difference',
                      legend_tracegroupgap = 250,
                      template = 'plotly+gridon',
                      plot_bgcolor='#ededed'
                      )
    
    fig.write_image('./res_plot/hourly_mean_boxplots/hourly_mean_box_plotly_'+spec+'.png')


def plot_sd_histo(data, stat,  id, alg, param, spec, heights):
    """
    plot histogram 

    Parameters
    ----------
    data, spike_data: list of Dataframes
        data to be plotted. If len(data)>1 then more histograms are plotted.
    stat, spec, id: str
        details for station name, instrument id, chemical specie from the ini file
    heights: list
        list of string with different sampling heights
    Returns
    -------
    None.
    """
    def plot_ax_hist(fig, ax, data, height):

        # eval meand and median values, spikes and write descriptive string
        spikes     = data[ data['spike_'+spec.lower()]==True ]['Stdev']
        non_spikes = data[ data['spike_'+spec.lower()]==False ]['Stdev']
        all_data   = data['Stdev']
        spikes_mean   = round(np.mean(spikes),2)
        spikes_median = round((np.median(spikes)),2)
        nbin          = round(len(data['Stdev'])**0.5)
        nbin_spike    = round(len(spikes)**0.5)
        all_mean      = round(np.mean(data['Stdev']),2)
        all_median    = round(np.median(data['Stdev']),2)
        mean_median_str = 'all mean = ' + str(all_mean) + '\nall median = ' + str(all_median) +'\nspikes mean = '+str(spikes_mean)+ '\nspikes median = '+str(spikes_median) 

        #ax2 = ax.twinx()
        ax.hist(spikes, bins = nbin_spike, density=True, log=False, label='spikes', color='gold', alpha =0.8,histtype='bar', ec='black')
        ax.axvline(spikes_mean, ls='-', color='coral', label ='mean')
        ax.axvline(spikes_median, ls='-.', color='coral', label='median')
        #ax2.tick_params('y', colors='orange')
        ax.hist(all_data, bins = nbin, density=True, log=False, label='all data', alpha= 0.5, color='cyan',histtype='bar', ec='black')
        ax.hist(non_spikes, bins = nbin, density=True, log=False, label='non-spike data', alpha=0.5, color='pink',histtype='bar', ec='black')
        ax.axvline(all_mean, ls='-', color='royalblue')
        ax.axvline(all_median, ls='-.', color='royalblue')
        ax.grid()
        ax.set_xlim([0, 0.5*(scoreatpercentile(spikes, 95) + scoreatpercentile(all_data, 95))])
        ax.set_xlabel('Stdev '+fmt.get_meas_unit(spec))
        ax.set_ylabel('Probability density')
        ax.set_yscale('log')
        ax.set_ylim(0.01,)
        #ax2.legend(loc=[0.72,0.6])
        ax.legend(loc='upper right')

        # write text boxes 
        t=ax.text(0.5,  0.9, height+' m', horizontalalignment='center', size='large', color='black',transform=ax.transAxes)                                              
        t.set_bbox(dict(facecolor='grey', alpha=0.3))
        t1=ax.text(0.83,  0.2, mean_median_str, horizontalalignment='center', size='large', color='black',transform=ax.transAxes)                                              
        t1.set_bbox(dict(facecolor='grey', alpha=0.3))

    file_path, file_suff, titlenm = fmt.format_file_plot_names(stat, spec, id)

    n_ax = len(data) #number of required axis

    fig, ax = plt.subplots(n_ax, 1, figsize = (8,4*n_ax))
    fig.suptitle(titlenm +'\n'+alg+' '+ param  )
    if n_ax>1:
        for i in range(len(ax)):
            plot_ax_hist(fig, ax[i], data[i], heights[i])

    else:
        plot_ax_hist(fig, ax, data[0], heights[0])

    plt.savefig(file_path+'hist/'+spec+'/hist_'+file_suff[0:len(file_suff)-4] +'_'+alg+'_'+param+'.pdf', format='pdf')
    plt.close(fig)
    
    
def plot_sd_time(df, stat, spec, id, heights):
    
    def plot_ax_time(ax, data, height):
            
        ax.scatter(data['Datetime'], data['Stdev'],s=.2, c='black')
        ax.scatter(data[data['spike_'+spec.lower()]==True]['Datetime'], data[data['spike_'+spec.lower()]==True]['Stdev'],s=.2, c='red')
        ax.grid()
        ax.set_ylim(0,)
        ax.set_ylabel('Stdev '+fmt.get_meas_unit(spec))
        t=ax.text(0.5,  0.9, height+' m', horizontalalignment='center', size='large', color='black',transform=ax.transAxes)                                              
        t.set_bbox(dict(facecolor='grey', alpha=0.3))
          
    file_path, file_suff, titlenm = fmt.format_file_plot_names(stat, spec, id)
    n_ax = len(df) #number of required axis
    
    if len(df[0])>0:
        month = list(df[0]['Datetime'])[0].month
        year  = list(df[0]['Datetime'])[0].year
        print(stat, id, spec, month, year)
    
        fig, ax = plt.subplots(n_ax, 1, figsize = (5,3*n_ax))
        fig.suptitle(titlenm + '   ' + str(fmt.get_month_str(month)) + ' ' + str(year) )
        
        if n_ax>1:
            for i in range(n_ax):   
                plot_ax_time(ax[i], df[i], heights[i])
        else:
             plot_ax_time(ax, df[0], heights[0])
        
        fig.autofmt_xdate()
        
        plt.savefig(file_path + 'monthly/'+spec+ '/timeseries_' +str(year)+'_'+str(month)+'_'+file_suff,format='pdf')
        plt.close(fig)

def plot_sd_event(df, stat,  id, alg, param, spec, heights, ev):
    """
    plot Stdev for a single event

    Parameters
    ----------
    df: list of Dataframes
        data to be plotted. If len(data)>1 then more graphs are plotted.
    stat, spec, id: str
        details for station name, instrument id, chemical specie from the ini file
    heights: list
        list of string with different sampling heights
    ev: list 
        list of datetime objects containing start and end date for the gien event
    Returns
    -------
    None.
    """
            
    def plot_ax_time(ax, data, height):
        ax.scatter(data['Datetime'], data['Stdev'],s=.2, c='black')
        ax.scatter(data[data['spike_'+spec.lower()]==True]['Datetime'], data[data['spike_'+spec.lower()]==True]['Stdev'],s=.2, c='red')
        ax.grid()
        ax.set_ylim(0,)
        ax.set_ylabel('Stdev '+fmt.get_meas_unit(spec))
        t=ax.text(0.5,  0.9, height+' m', horizontalalignment='center', size='large', color='black',transform=ax.transAxes)                                              
        t.set_bbox(dict(facecolor='grey', alpha=0.3))
        
    start_date = ev[0]
    end_date   = ev[1]
    
    file_path, file_suff, titlenm = fmt.format_file_plot_names(stat, spec, id)
    n_ax = len(df) #number of required axis
    
    if len(df[0])>0:
        sel_heights = [] # selected heights for plotting (i.e. heights with non-emply datasets)
        sel_df = []
        event_df = [] # dataframe to store selected events from df
        for i in range(len(df)): 
            event_df.append(df[i][(df[i]['Datetime']>=start_date) & (df[i]['Datetime']<=end_date)]) # select event
            if len(event_df[i])==0: # reduce number of axis in case of empty dataset
                n_ax=n_ax-1
            else:
                sel_heights.append(heights[i]) # add height[i] to selected heights if dataset at haight[i] is non-empty
                sel_df.append(event_df[i]) # add event_df[i] to selected dataframes 
                
        if n_ax>0: #plot only if at least one non-empty dataset is present
            print(stat, id, spec, ev[0], ev[1])
            
            fig, ax = plt.subplots(n_ax, 1, figsize = (5,4*n_ax))
            fig.suptitle(titlenm + '   ' + '   '+alg+' '+ param+'\nEVENT ' +  str(ev[0]) + ' - ' + str(ev[1]) )
            
            if n_ax>1: # plot multiplt heights on single figure
                for i in range(n_ax):
                    plot_ax_time(ax[i], sel_df[i], sel_heights[i])
            else: # plot single height
                 plot_ax_time(ax, sel_df[0], sel_heights[0])
            
            fig.autofmt_xdate()
            
            plt.savefig(file_path + 'events/'+spec+ '/event_' +str(start_date.day)+'-'+str(start_date.month)+'-'+str(start_date.year)+'_'+ alg+'_'+param+'_'+file_suff,format='pdf')
            plt.close(fig)
            
def plot_conc_sd_event(df, stat, id, alg, param, spec, heights, ev):
    """
    plot concentration and Stdev for a single event

    Parameters
    ----------
    df: list of Dataframes
        data to be plotted. If len(data)>1 then more graphs are plotted.
    stat, spec, id: str
        details for station name, instrument id, chemical specie from the ini file
    heights: list
        list of string with different sampling heights
    ev: list 
        list of datetime objects containing start and end date for the gien event
    Returns
    -------
    None.
    """

    def plot_ax_time(ax, data, height):
        ax[0].scatter(data['Datetime'], data['Stdev'],s=.2, c='black')
        ax[0].scatter(data[data['spike_'+spec.lower()]==True]['Datetime'], data[data['spike_'+spec.lower()]==True]['Stdev'],s=.2, c='red')
        ax[0].set_ylabel('Stdev '+fmt.get_meas_unit(spec))
        ax[0].set_ylim(0,)

        ax[1].scatter(data['Datetime'], data[spec.lower()],s=.2, c='black')
        ax[1].scatter(data[data['spike_'+spec.lower()]==True]['Datetime'], data[data['spike_'+spec.lower()]==True][spec.lower()],s=.2, c='red')
        ax[1].set_ylabel('['+spec.upper()+'] '+fmt.get_meas_unit(spec))
       
        #t=ax[0].text(0.5,  0.9, height+' m', horizontalalignment='center', size='large', color='black',transform=ax.transAxes)                                              
        #t.set_bbox(dict(facecolor='grey', alpha=0.3))
        for ax in axs:
            ax.grid()
            ax.label_outer()

    start_date = ev[0]
    end_date   = ev[1]
    file_path, file_suff, titlenm = fmt.format_file_plot_names(stat, spec, id)
    print('Plot event timeseries', stat, id, spec)
    
    n_heights = len(heights)-1 # used to select only the highest sampling level in case of more sampling heights are provided
    if len(df[n_heights])>0:
        
        event_df = df[n_heights][(df[n_heights]['Datetime']>=start_date) & (df[n_heights]['Datetime']<=end_date)] # select event
        
        fig = plt.figure()
        fig.suptitle(titlenm + 'h=' + heights[n_heights] +'   '+ alg +' '+ param +'\nEVENT '+ str(ev[0]) +' - '+ str(ev[1]) )
        
        gs = fig.add_gridspec(2, hspace=0)
        axs = gs.subplots(sharex=True)

        plot_ax_time(axs, event_df, heights[n_heights])

        fig.autofmt_xdate()

        date_str = str(start_date.year)+'-'+str(start_date.month)+'-'+str(start_date.day)
        plt.savefig(file_path + 'events/'+date_str+'/'+spec+ '/event_std_conc_' +date_str+'_'+ alg+'_'+param+'_'+file_suff,format='pdf')
        plt.close(fig)

def plot_conc_sd_event_histo(df, stat, id, alg, param, spec, heights, ev):
    """
    plot concentration and Stdev histograms for a single event

    Parameters
    ----------
    df: list of Dataframes
        data to be plotted. If len(data)>1 then more graphs are plotted.
    stat, spec, id: str
        details for station name, instrument id, chemical specie from the ini file
    heights: list
        list of string with different sampling heights
    ev: list 
        list of datetime objects containing start and end date for the gien event
    Returns
    -------
    None.
    """
    def plot_ax_histo(ax, data, height, var):

        spikes     = data[ data['spike_'+spec.lower()]==True ][var]
        non_spikes = data[ data['spike_'+spec.lower()]==False ][var]
       # all_data   = data[var]
       # spikes_mean   = round(np.mean(spikes),2)
        spikes_median = round((np.median(spikes)),2)
        nbin_nospike  = round(len(non_spikes)**0.5)
        nbin_spike    = round(len(spikes)**0.5)
        if ((nbin_nospike>0) & (nbin_spike>0)):
           # nospike_mean      = round(np.mean(non_spikes),2)
            nospike_median    = round(np.median(non_spikes),2)
            #mean_median_str = 'all mean = ' + str(all_mean) + '\nall median = ' + str(all_median) +'\nspikes mean = '+str(spikes_mean)+ '\nspikes median = '+str(spikes_median) 

            ax.hist(spikes, bins = nbin_spike, density=True, log=False, label='spikes', color='gold', alpha =0.6,histtype='bar', ec='black')
            #ax.axvline(spikes_mean, ls='-', color='coral', label ='mean')
            ax.axvline(spikes_median, ls='-.', color='coral', label='median spikes')
            #ax.hist(all_data, bins = nbin, density=True, log=False, label='all data', alpha= 0.5, color='cyan',histtype='bar', ec='black')
            ax.hist(non_spikes, bins = nbin_nospike, density=True, log=False, label='non-spike', alpha=0.8, color='pink',histtype='bar')
            #ax.axvline(all_mean, ls='-', color='royalblue')
            ax.axvline(nospike_median, ls='-.', color='magenta', label='median non-spike')
            ax.set_xlabel(var+' '+fmt.get_meas_unit(spec))
            ax.set_ylabel('Probability density')
            ax.set_yscale('log')
            #ax.set_xlim(right=scoreatpercentile(spikes, 99))
            #ax.set_ylim(0.01,)
            ax.grid()
            # write text boxes
            # t=ax.text(0.5,  0.9, height+' m', horizontalalignment='center', size='large', color='black',transform=ax.transAxes)
            # t.set_bbox(dict(facecolor='grey', alpha=0.3))
            # t1=ax[1].text(0.83,  0.2, mean_median_str, horizontalalignment='center', size='large', color='black',transform=ax.transAxes)
            # t1.set_bbox(dict(facecolor='grey', alpha=0.3))

            #t=ax[0].text(0.5,  0.9, height+' m', horizontalalignment='center', size='large', color='black',transform=ax.transAxes)
            #t.set_bbox(dict(facecolor='grey', alpha=0.3))

    start_date = ev[0]
    end_date   = ev[1]
    file_path, file_suff, titlenm = fmt.format_file_plot_names(stat, spec, id)
    print('Plot event histogram', stat, id, spec)
    n_heights = len(heights)-1 # used to select only the highest sampling level in case of more sampling heights are provided

    if len(df[n_heights])>0:

        event_df = df[n_heights][(df[n_heights]['Datetime']>=start_date) & (df[n_heights]['Datetime']<=end_date)] # select event

        if len(event_df)>0: #plot histogram only if the event dataset is non-empty
           fig, ax = plt.subplots(2, 1, figsize = (5,8))
           fig.suptitle(titlenm + ' height=' + heights[n_heights] + ' m'+'   '+ alg +' '+ param +'\nEVENT '+ str(ev[0]) +' - '+ str(ev[1]) )

           plot_ax_histo(ax[0], event_df, heights[n_heights], 'Stdev')
           plot_ax_histo(ax[1], event_df, heights[n_heights], spec.lower())
           ax[0].legend(loc='upper right')
           date_str = str(start_date.year)+'-'+str(start_date.month)+'-'+str(start_date.day)
           plt.savefig(file_path + 'events/'+date_str+'/'+spec+ '/event_hist_std_conc_' +date_str+'_'+ alg+'_'+param+'_'+file_suff,format='pdf')
           plt.close(fig)

def plot_conc_event(df, stat,  id, alg, param, spec, heights, ev):
    """
    plot concentration for a single event

    Parameters
    ----------
    df: list of Dataframes
        data to be plotted. If len(data)>1 then more graphs are plotted.
    stat, spec, id: str
        details for station name, instrument id, chemical specie from the ini file
    heights: list
        list of string with different sampling heights
    ev: list 
        list of datetime objects containing start and end date for the given event
    Returns
    -------
    None.
    """
            
    def plot_ax_time(ax, data, height):
        ax.scatter(data['Datetime'], data[spec.lower()],s=.2, c='black')
        ax.scatter(data[data['spike_'+spec.lower()]==True]['Datetime'], data[data['spike_'+spec.lower()]==True][spec.lower()],s=.2, c='red')
        ax.grid()
        ax.set_ylabel(spec.lower()+' '+fmt.get_meas_unit(spec))
        t=ax.text(0.5,  0.9, height+' m', horizontalalignment='center', size='large', color='black',transform=ax.transAxes)                                              
        t.set_bbox(dict(facecolor='grey', alpha=0.3))
        
    start_date = ev[0]
    end_date   = ev[1]
    
    file_path, file_suff, titlenm = fmt.format_file_plot_names(stat, spec, id)
    n_ax = len(df) #number of required axis
    
    if len(df[0])>0:
        sel_heights = [] # selected heights for plotting (i.e. heights with non-emply datasets)
        sel_df = []
        event_df = [] # dataframe to store selected events from df
        for i in range(len(df)): 
            event_df.append(df[i][(df[i]['Datetime']>=start_date) & (df[i]['Datetime']<=end_date)]) # select event
            if len(event_df[i])==0: # reduce number of axis in case of empty dataset
                n_ax=n_ax-1
            else:
                sel_heights.append(heights[i]) # add height[i] to selected heights if dataset at haight[i] is non-empty
                sel_df.append(event_df[i]) # add event_df[i] to selected dataframes 
                
        if n_ax>0: #plot only if at least one non-empty dataset is present
            print(stat, id, spec, ev[0], ev[1])
            
            fig, ax = plt.subplots(n_ax, 1, figsize = (5,4*n_ax))
            fig.suptitle(titlenm + '   ' + '   '+alg+' '+ param+'\nEVENT ' +  str(ev[0]) + ' - ' + str(ev[1]) )
            
            if n_ax>1: # plot multiplt heights on single figure
                for i in range(n_ax):
                    plot_ax_time(ax[i], sel_df[i], sel_heights[i])
            else: # plot single height
                 plot_ax_time(ax, sel_df[0], sel_heights[0])
            
            fig.autofmt_xdate()
            date_str = str(start_date.year)+'-'+str(start_date.month)+'-'+str(start_date.day)
            plt.savefig(file_path + 'events/'+date_str+'/'+spec+ '/event_conc_' +str(start_date.day)+'-'+str(start_date.month)+'-'+str(start_date.year)+'_'+ alg+'_'+param+'_'+file_suff,format='pdf')
            plt.close(fig)
            
def plot_conc_event_PIQc(df, stat,  id, alg, param, spec, heights, ev, mode, quant):
    """
    plot concentration for a single event

    Parameters
    ----------
    df: list of Dataframes
        data to be plotted. If len(data)>1 then more graphs are plotted.
    stat, spec, id: str
        details for station name, instrument id, chemical specie from the ini file
    heights: list
        list of string with different sampling heights
    ev: list 
        list of datetime objects containing start and end date for the given event
    mode: str
        'single' or 'distr' . Choose wether to define "high" spikes according to difference of each point rescpect to the baseline or to the quartiles of the difference distribution
    quant: float
        quantile to evaluate the threshold for high spikes               
    Returns
    -------
    None.
    """

    def plot_ax_time(ax, data, height):
        ax.scatter(data['Datetime'], data[spec.lower()],s=.2, c='black')

        spike_frame = data[data['spike_'+spec.lower()+'_PIQc']==True]
        ax.scatter(spike_frame['Datetime'], spike_frame[spec.lower()],s=.2, c='red')
        
        min_diff = stats.get_threshold(data, spec, mode, quant)
        high_spike_frame = data[ data['spike_amplitude_'+spec.lower()+'_PIQc']>min_diff ]
        ax.scatter(high_spike_frame['Datetime'], high_spike_frame[spec.lower()],s=.2, c='chartreuse')

        ax.plot(data['Datetime'], data[spec.lower()+'_rolling_mean'], ls='-', lw=.5)
        ax.grid()
        ax.set_ylabel(spec.lower()+' '+fmt.get_meas_unit(spec))
        t=ax.text(0.5,  0.9, height+' m', horizontalalignment='center', size='large', color='black',transform=ax.transAxes)                                              
        t.set_bbox(dict(facecolor='grey', alpha=0.3))

    start_date = ev[0]
    end_date   = ev[1]
    file_path, file_suff, _ = fmt.format_file_plot_names(stat, spec, id)
    titlenm = spec +' at '+stat +' ' +id
    n_ax = len(df) #number of required axis
    if len(df[0])>0:
        sel_heights = [] # selected heights for plotting (i.e. heights with non-emply datasets)
        sel_df = []
        event_df = [] # dataframe to store selected events from df
        for i in range(len(df)): 
            event_df.append(df[i][(df[i]['Datetime']>=start_date) & (df[i]['Datetime']<=end_date)]) # select event
            if len(event_df[i])==0: # reduce number of axis in case of empty dataset
                n_ax=n_ax-1
            else:
                sel_heights.append(heights[i]) # add height[i] to selected heights if dataset at haight[i] is non-empty
                sel_df.append(event_df[i]) # add event_df[i] to selected dataframes 

        if n_ax>0: #plot only if at least one non-empty dataset is present
            print(stat, id, spec, ev[0], ev[1])

            fig, ax = plt.subplots(n_ax, 1, figsize = (5,4*n_ax))
            fig.suptitle(titlenm + '    PIQc\nEVENT ' +  str(ev[0]) + ' - ' + str(ev[1]) )

            if n_ax>1: # plot multiplt heights on single figure
                for i in range(n_ax):
                    plot_ax_time(ax[i], sel_df[i], sel_heights[i])
            else: # plot single height
                 plot_ax_time(ax, sel_df[0], sel_heights[0])

            fig.autofmt_xdate()
            plt.savefig(file_path + 'events/PIQc/event_conc_' +str(start_date.day)+'-'+str(start_date.month)+'-'+str(start_date.year)+'_PIQc_'+file_suff,format='pdf')
            plt.close(fig)

def plot_conc_event_PIQc_plotly(df, stat,  id, alg, param, spec, heights, ev, mode, quant):
    """
    plot concentration for a single event

    Parameters
    ----------
    df: list of Dataframes
        data to be plotted. If len(data)>1 then more graphs are plotted.
    stat, spec, id: str
        details for station name, instrument id, chemical specie from the ini file
    heights: list
        list of string with different sampling heights
    ev: list 
        list of datetime objects containing start and end date for the given event
    mode: str
        'single' or 'distr' . Choose wether to define "high" spikes according to difference of each point rescpect to the baseline or to the quartiles of the difference distribution
    quant: float
        quantile to evaluate the threshold for high spikes 
    Returns
    -------
    None.
    """
            
    def plot_ax_time(row, fig, data, height):
        fig.add_trace( go.Scatter(x=data['Datetime'], y=data[spec.lower()], mode = "lines",  line = {'color' : 'cornflowerblue'}, name = '1-min data'), row=row, col=1)
        fig.add_trace( go.Scatter(x=data['Datetime'], y=data[spec.lower()+'_rolling_mean'], mode = "lines", line = {'color' : 'blue'}, name = 'baseline'), row=row, col=1)

        spike_frame = data[data['spike_'+spec.lower()+'_PIQc']==True]
        fig.add_trace( go.Scatter(x=spike_frame['Datetime'], y=spike_frame[spec.lower()], mode = "markers", marker={'color':'red'}, name='low spikes'), row=row, col=1)

        min_diff = stats.get_threshold(data, spec, mode, quant)
        high_spike_frame = data[ data['spike_amplitude_'+spec.lower()+'_PIQc']>min_diff ]
        fig.add_trace( go.Scatter(x=high_spike_frame['Datetime'], y=high_spike_frame[spec.lower()], mode = "markers", marker={'color':'green'}, name='high spikes'), row=row, col=1)
        fig.update_layout(font={'size':25})
#        ax.set_ylabel(spec.lower()+' '+fmt.get_meas_unit(spec))
#        t=ax.text(0.5,  0.9, height+' m', horizontalalignment='center', size='large', color='black',transform=ax.transAxes)                                              
#        t.set_bbox(dict(facecolor='grey', alpha=0.3))
        
    start_date = ev[0]
    end_date   = ev[1]
    file_path, file_suff, _ = fmt.format_file_plot_names(stat, spec, id)
    titlenm = spec +' at '+stat +' ' +id
    n_ax = len(df) #number of required axis
    if len(df[0])>0:
        sel_heights = [] # selected heights for plotting (i.e. heights with non-emply datasets)
        sel_df = []
        event_df = [] # dataframe to store selected events from df
        for i in range(len(df)): 
            event_df.append(df[i][(df[i]['Datetime']>=start_date) & (df[i]['Datetime']<=end_date)]) # select event
            if len(event_df[i])==0: # reduce number of axis in case of empty dataset
                n_ax=n_ax-1
            else:
                sel_heights.append(heights[i]) # add height[i] to selected heights if dataset at haight[i] is non-empty
                sel_df.append(event_df[i]) # add event_df[i] to selected dataframes 

        if n_ax>0: #plot only if at least one non-empty dataset is present
            print(stat, id, spec, ev[0], ev[1])
            
            fig = make_subplots(rows=n_ax, cols=1)
            fig.update_layout(title_text=titlenm + '    PIQc\nEVENT ' +  str(ev[0]) + ' - ' + str(ev[1]))            
            for i in range(n_ax):
                plot_ax_time(i+1, fig, sel_df[i], sel_heights[i])

            fig.write_html(file_path + 'events/PIQc/event_conc_' +str(start_date.day)+'-'+str(start_date.month)+'-'+str(start_date.year)+'_PIQc_'+file_suff[0:-4]+'.html')
            

def plot_sd_qqplot(data, stat, id, alg, param, spec, heights):   

    file_path, file_suff, titlenm = fmt.format_file_plot_names(stat, spec, id)

    n_ax = len(data) #number of required axis

    fig, ax = plt.subplots(1, n_ax, figsize = (4*n_ax,4))
    fig.suptitle('Q-Q plot '+ titlenm +'\n'+alg+' '+ param  )

    if n_ax>1:
        for i in range(len(ax)):
            spikes     = data[i][ data[i]['spike_'+spec.lower()]==True ]['Stdev']
            non_spikes = data[i][ data[i]['spike_'+spec.lower()]==False ]['Stdev']
            all_data   = data[i]['Stdev']
            stats.qqplot(spikes, non_spikes, ax=ax[i], height=heights[i])

    else:
        spikes     = data[0][ data[0]['spike_'+spec.lower()]==True ]['Stdev']
        non_spikes = data[0][ data[0]['spike_'+spec.lower()]==False ]['Stdev']
        all_data   = data[0]['Stdev']
        stats.qqplot(spikes, non_spikes, ax=ax, height=heights[0])

    plt.savefig(file_path+'qqplot/qqplot_'+file_suff[0:len(file_suff)-4] +'_'+alg+'_'+param+'.pdf', format='pdf')
    plt.close(fig)

def plot_heatmap_monthly_diff(algo_names, algos, species):
    center = [-0.1,-2,-1] # WMO limits for colormaps
    labels = ['','','','','','','','','','','','','','','','','','','','','','','','']

    vmin=[-2,-10,-5] #max values for heatmap cbar for each specie
    fig, ax = plt.subplots(3,2, figsize=(10,8))
    for i in range(3):
        for j in range(2):
            data =pd.read_csv('./heatmap_tables/heatmap_table_'+str(algo_names[j])+'_'+str(algos[j])+'_'+str(species[i])+'.csv', sep = ' ',index_col=0)
            if j == 0:
                cbar=False
            else:
                cbar=True
            sea.heatmap(data, ax = ax[i][j], cbar=cbar,vmin = vmin[i], vmax=0, cmap=plt.cm.coolwarm_r, center=center[i],xticklabels=labels)
        if i == 1: # change labels only for bottom plots
            labels = ['','Feb\n\'19','','Apr\n\'19','','Jun\n\'19','','Aug\n\'19','','Oct\n\'19','','Dec\n\'19','','Feb\n\'20','','Apr\n\'20','','Jun\n\'20','','Aug\n\'20','','Oct\n\'20','','Dec\n\'20']
    plt.savefig('./heatmap_plot/heatmap_'+str(algo_names[j])+'_'+str(algos[j])+'.pdf')
    
    


def plot_heatmap_frequencies(algo, param, species):
    
    labels = ['','Feb\n\'19','','Apr\n\'19','','Jun\n\'19','','Aug\n\'19','','Oct\n\'19','','Dec\n\'19','','Feb\n\'20','','Apr\n\'20','','Jun\n\'20','','Aug\n\'20','','Oct\n\'20','','Dec\n\'20']

    for i in range(3):
        fig, ax = plt.subplots(1,2, figsize=(8,4), gridspec_kw={'width_ratios': [10, 1]}) # create two subplots, one for the heatmap and the other for the custom colorbar
        fig.suptitle('Percentage of spike detected for each month\n'+species[i] + ' - '+algo+' '+param)
       
        data =pd.read_csv('./heatmap_tables/heatmap_table_freq_'+str(algo)+'_'+str(param)+'_'+str(species[i])+'.csv', sep = ' ',index_col=0)
        cmap, bins, ncolors = cmap_discretize(plt.cm.viridis,8)
        sea.heatmap(100*data, ax = ax[0], 
                    cbar=False, 
                    vmin = 0, vmax=100, 
                    cmap=cmap, 
                    xticklabels=labels,
                    linewidths=0.01,
                    linecolor='black',
                    annot=True, fmt=".1f", annot_kws={'fontsize':5})
        
        # define and plot custom colorbar
        norm = matplotlib.colors.BoundaryNorm(boundaries=bins, ncolors=ncolors-1 )
        cb=matplotlib.colorbar.ColorbarBase(ax[1], 
                                cmap=cmap,
                                boundaries=  bins ,
                                extend='both',
                                ticks=bins,
                                spacing='uniform',
                                drawedges=False)
        cb.ax.set_yticklabels([str(int(100*b))+'%' for b in bins[1:-1]])
  
        # draw bold hlines to separate different instruments
        indexes=data.index.to_list()
        hlines_indexes=[]
        for j in range(1, len(indexes)):
            if indexes[j][0:7]!=indexes[j-1][0:7]: # if the jth instrument is different from the j-1th store the line number in the hlines_indexes list
                hlines_indexes.append(j)
        ax[0].hlines(hlines_indexes, *ax[0].get_xlim(), colors='white') # draw hlines
        
        # format and save figure
        sea.set_style("dark")
        plt.tight_layout()
        plt.savefig('./heatmap_plot/heatmap_'+species[i]+'_'+str(algo)+'_'+str(param)+'.pdf')
        plt.close()

def plot_heatmap_coverage(algo, species):
    
    labels = ['','Feb\n\'19','','Apr\n\'19','','Jun\n\'19','','Aug\n\'19','','Oct\n\'19','','Dec\n\'19','','Feb\n\'20','','Apr\n\'20','','Jun\n\'20','','Aug\n\'20','','Oct\n\'20','','Dec\n\'20']

    for i in range(3):
        fig, ax = plt.subplots(1,2, figsize=(8,4), gridspec_kw={'width_ratios': [10, 1]}) # create two subplots, one for the heatmap and the other for the custom colorbar
        fig.suptitle('Percentage of data with respect to total minutes for each month\n'+species[i])
       
        data =100*pd.read_csv('./heatmap_tables/heatmap_table_coverage_'+str(species[i])+'.csv', sep = ' ',index_col=0)
        cmap, bins, ncolors = cmap_discretize(plt.cm.viridis,8,list_indices=[0, 0.10, 0.20, 0.40, 0.60, 0.70, 0.80, 0.90, 1])
        sea.heatmap(data, ax = ax[0], 
                    cbar=False, 
                    vmin = 0, vmax=100, 
                    cmap=cmap, 
                    xticklabels=labels,
                    linewidths=0.01,
                    linecolor='black',
                    annot=True, fmt=".1f", annot_kws={'fontsize':5})
        
        # define and plot custom colorbar
        norm = matplotlib.colors.BoundaryNorm(boundaries=bins, ncolors=ncolors-1 )
        cb=matplotlib.colorbar.ColorbarBase(ax[1], 
                                cmap=cmap,
                                boundaries=  bins ,
                                extend='both',
                                ticks=bins,
                                spacing='uniform',
                                drawedges=False)
        cb.ax.set_yticklabels([str(int(100*b))+'%' for b in bins[1:-1]])
  
        # draw bold hlines to separate different instruments
        indexes=data.index.to_list()
        hlines_indexes=[]
        for j in range(1, len(indexes)):
            if indexes[j][0:7]!=indexes[j-1][0:7]: # if the jth instrument is different from the j-1th store the line number in the hlines_indexes list
                hlines_indexes.append(j)
        ax[0].hlines(hlines_indexes, *ax[0].get_xlim(), colors='white') # draw hlines
        
        # format and save figure
        sea.set_style("dark")
        plt.tight_layout()
        plt.savefig('./heatmap_plot/heatmap_coverage_'+species[i]+'.pdf')
        plt.close()


def cmap_discretize(cmap, N, list_indices=[0, 0.01, 0.05, 0.10, 0.20, 0.40, 0.60, 0.80, 1]):
    """Return a discrete colormap from the continuous colormap cmap.

        cmap: colormap instance, eg. cm.jet. 
        N: number of colors.

    Example
        x = resize(arange(100), (5,100))
        djet = cmap_discretize(cm.jet, 5)
        imshow(x, cmap=djet)
    """

    if type(cmap) == str:
        cmap = plt.get_cmap(cmap)
    colors_i = np.concatenate((np.linspace(0, 1., N), (0.,0.,0.,0.)))
    colors_rgba = cmap(colors_i)
    indices = np.linspace(0, 1., N+1)
    indices = np.array(list_indices)
    cdict = {}
    for ki,key in enumerate(('red','green','blue')):
        cdict[key] = [ (indices[i], colors_rgba[i-1,ki], colors_rgba[i,ki]) for i in range(N+1) ]
    # Return colormap object.
    return matplotlib.colors.LinearSegmentedColormap(cmap.name + "_%d"%N, cdict, 1024), indices.tolist(), len(indices)

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
