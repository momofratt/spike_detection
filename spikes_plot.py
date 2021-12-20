#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 12:02:42 2021

@author: Cosimo Fratticioli
@contact: c.fratticioli@isac.cnr.it
"""
import matplotlib.pyplot as plt 
import matplotlib.ticker as mtick
import spikes_formatting_functions as fmt
import spikes_data_selection_functions as sel
import spikes_statistics as stats
import numpy as np 
from scipy.stats import scoreatpercentile
import seaborn as sea
import pandas as pd


monthly_range_CO_dict  = {'SAC':[90,240], 'CMN':[90,150], 'IPR':[120,470], 'KIT':[100,300], 'JUS':[90,350], 'JFJ':[90,150],'PUI':[],'UTO':[80,170]}
monthly_range_CO2_dict = {'SAC':[405,440], 'CMN':[400,425], 'IPR':[405,480], 'KIT':[405,480], 'JUS':[410,460], 'JFJ':[400,425],'PUI':[390,430],'UTO':[400,425]}
monthly_range_CH4_dict = {'SAC':[1950,2050], 'CMN':[1900,2000], 'IPR':[1975,2150], 'KIT':[1950,2150], 'JUS':[1950,2100], 'JFJ':[1900,1975],'PUI':[1925,2030],'UTO':[1925,2025]}
daily_range_CO2_dict = {'SAC':[410,430], 'CMN':[400,425], 'IPR':[410,450], 'KIT':[410,440], 'JUS':[400,450], 'JFJ':[400,420],'PUI':[400,430],'UTO':[400,430]}
daily_range_CH4_dict = {'SAC':[1950,2050], 'CMN':[1930,1980], 'IPR':[1975,2150], 'KIT':[1950,2075], 'JUS':[1950,2100], 'JFJ':[1920,1955],'PUI':[1920,2010],'UTO':[1955,2010]}
daily_range_CO_dict  = {'SAC':[90,180], 'CMN':[90,150], 'IPR':[100,400], 'KIT':[125,200], 'JUS':[90,260], 'JFJ':[100,130],'PUI':[],'UTO':[85,145]}

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
    def plot_daily_cycle(season_data, ax, alg, params):
        non_spiked=np.array(season_data[-1])
        min, max = 0, 0
        for j in range(len(season_data)-1):
            delta = -non_spiked+np.array(season_data[j])
            ax[0].plot(delta, label = alg +' '+params[j])
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
            season_day_data = sel.get_daily_season_data(stat, id, alg, params, spec, height,season[1])
            plot_daily_cycle(season_day_data, ax[i], alg, params)
        if log:
            log_folder = 'log/'
            log_suff='_logscale'

        fig.suptitle("Daily mean cycle of concentration: absolute values and difference between non-spiked and spiked data\n"+spec+' at '+stat+' '+id+'   height=' + height + ' m   season='+season[0]+season[2])
        plt.savefig('./res_plot/'+stat+'/daily_cycle/'+log_folder+'seasonal_daily_cycle_'+season[0]+'_'+stat+'_'+spec+'_'+id+'_h'+height+log_suff+'.pdf', format='pdf', bbox_inches="tight")
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
        ax[0].set_ylabel('Concentration difference '+fmt.get_meas_unit(spec))
        ax[1].set_ylabel('Concentration '+fmt.get_meas_unit(spec))
        ax[1].legend(bbox_to_anchor=(1,1), loc="upper left")

        for a in ax:
            a.grid(which='major')
            a.set_xticks(np.arange(0,23,2))
            #months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
            labels = ['Jan\n\'19','Mar\n\'19','May\n\'19','Jul\n\'19','Sep\n\'19','Nov\n\'19','Jan\n\'20','Mar\n\'20','May\n\'20','Jul\n\'20','Sep\n\'20','Nov\n\'20']
            a.set_xticklabels(labels)
        ax[0].grid(b=True, which='minor', linestyle='-', alpha=0.2)

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
        list of datetime objects containing start and end date for the gien event
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
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
