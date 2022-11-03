#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  1 12:58:15 2021

@author: Cosimo Fratticioli
@contact: c.fratticioli@isac.cnr.it
"""

import numbers
import numpy as np
import matplotlib.pyplot as plt
import spikes_formatting_functions as fmt
import pandas as pd 
from configparser import ConfigParser

min_ampl_dict = {'CO2': 0.5, 'CO':2, 'CH4': 2}

def plot_BFOR_parameters(stat, inst_id, algorithms, spec, height, high_spikes, high_spikes_mode, quant):
    """
    plot results from statistical analysis of PIQc and automatic flagging
    Parameters
    ----------
    stat : str
        station name.
    inst_id : str
        instrument id.
    algorithms : 2D list
        list containing algorithms names and parameters values.
    spec : str
        specie.
    height : str
        sampling height.
    high_spikes : bool
        enable/disable analysis of "high" spikes.
    high_spikes_mode: str
        'single' or 'distr' . Choose wether to define "high" spikes according to difference of each point respect to the baseline or to the quartiles of the difference distribution
    quant: float
        quantile to evaluate the threshold for high spikes
    Returns
    -------
    None.
    """
    for i in range(len(algorithms)):
        alg = algorithms[i][0] # read current algorithm name (REBS or SD)
        params = algorithms[i][1:len(algorithms[i])] # get list of parameters
        B  = np.empty(0)
        H  = np.empty(0)
        F  = np.empty(0)
        OR = np.empty(0)
        ORSS = np.empty(0)
        stdev_logOR = np.empty(0)
        min_a, min_b, min_c, min_d = 1E10,1E10,1E10,1E10
        for param in params:
            infile_spiked = './data-minute-spiked/' + stat +'/' + fmt.get_L1_file_name(stat, height, spec, inst_id)+'_'+ alg +'_'+ param + '_spiked_PIQc_mean'
            frame = pd.read_csv(infile_spiked, sep=';')

            if high_spikes:
               frame = add_high_spikes_col(frame, spec, high_spikes_mode, quant)
               observed = 'high_spike_'+spec.lower()+'_PIQc' # observed spikes
               high_spikes_str  = ' - high spikes (>'+str(min_ampl_dict[spec])+' '+fmt.get_meas_unit(spec)+')'
               high_spikes_suff = '_high'
            else:
               high_spikes_str  = ''
               high_spikes_suff = ''
               observed = 'spike_'+spec.lower()+'_PIQc' # observed spikes
            forecast = 'spike_'+spec.lower() # forecasted spikes

            a = len(frame[ (frame[forecast]==True ) & (frame[observed]==True ) ])
            b = len(frame[ (frame[forecast]==True ) & (frame[observed]==False) ])
            c = len(frame[ (frame[forecast]==False) & (frame[observed]==True ) ])
            d = len(frame[ (frame[forecast]==False) & (frame[observed]==False) ])
            B  = np.append( B, (a+b)/(a+c))
            H  = np.append( H, a/(a+c))
            F  = np.append( F, b/(b+d))
            err=0
            if (b==0) | (c==0):
                print(alg,param,'ZERO VALUE: b=',b,'c=',c)
                OR =np.append( OR, np.nan)    
                ORSS = np.append(ORSS, np.nan)
                stdev_logOR = np.append(stdev_logOR,0)
            else:
                OR = np.append( OR, a*d/b/c)
                ORSS = np.append(ORSS, (a*d-b*c)/(a*d+b*c))
                if(a!=0) & (d!=0):
                    stdev_logOR = np.append(stdev_logOR,(1/a + 1/b + 1/c + 1/d)**0.5)
                else:
                    stdev_logOR = np.append(stdev_logOR,0)
                    print(alg,param,'ZERO VALUE: a=',a,'d=',d)
                if (a<5) |(b<5) |(c<5) |(d<5):
                    print(alg,param,'COUNT < 5:',a,b,c,d)
                    OR[-1]=np.nan
                    ORSS[-1]=np.nan
                    err=1
            logOR=np.log(OR)    
            if a < min_a:
                min_a=a
            if b < min_b:
                min_b=b
            if c < min_c:
                min_c=c
            if d < min_d:
                min_d=d

        # # plot parameters
        fig, ax = plt.subplots(1,1)
        fig.suptitle('Statistical parameters\nstation: '+stat+'  h='+str(height)+'   spec='+spec+high_spikes_str)
        labels=[str(p) for p in params]

        ax.plot(H, label='hit rate', color = 'C1', ls='-')
        ax.plot(F, label='false alarm rate', color = 'C1', ls='-')
        ax.plot(H-F, label = 'H-F', color='C1')
        ax.plot(ORSS, label = 'ORSS', color = 'C3')

        ax.set_xticks(np.arange(0,len(params),1))
        ax.set_xticklabels(labels)
        ax.grid()
        ax.legend(loc=[1.1,0.82])
        # t=ax.text(1.3,  0.2, 'min a= '+str(min_a)+'\nmin b= '+str(min_b)+'\nmin c= '+str(min_c)+'\nmin d= '+str(min_d), horizontalalignment='center', size='large', color='black',transform=ax.transAxes)                                              
        # t.set_bbox(dict(facecolor='grey', alpha=0.3))
        ax.set_xlabel(alg)
        ax.set_ylim(0,1.05)
        if (min(ORSS)<0) & (min(ORSS)>-100):
            ax.set_ylim(min(ORSS)-0.1,1.05)

        if spec=='CO':
            if alg=='REBS':
                ax.axvline(7,c='black',ls='--')  
            elif alg=='SD':
                ax.axvline(6,c='black',ls='--')
        else:
            if alg=='REBS':
                ax.axvline(2,c='black',ls='--')  
            elif alg=='SD':
                ax.axvline(2,c='black',ls='--')
        ax2 = ax.twinx()
        ax2.plot(B, label = 'BIAS', color = 'C2')
        #ax2.errorbar(np.arange(0,len(logOR),1), logOR, stdev_logOR,elinewidth=1, capsize =5, ls='none', fmt="o", color = 'C2', label = 'log OR')
        ax2.axhline(1, c='C2',ls=':',lw=1)
        ax2.tick_params('y',which='both', colors='C2')
        ax2.legend(loc=[1.1,0.7])
        if max(B)>10:
            ax2.set_yscale('log')

        # write infos on spike percentage
        stat_text = 'PIQc spikes = '+str(round((a+c)/(a+b+c+d)*100,2))+'%'
        t1=ax.text(1.05,  0.05, stat_text, horizontalalignment='left', size='large', color='black',transform=ax.transAxes)
        t1.set_bbox(dict(facecolor='tan', alpha=0.3))

        plt.savefig('res_plot/'+stat+'/bfor_parameters/bfor_parameters_'+stat+'_'+spec+'_h'+str(height)+'_'+alg+high_spikes_suff+'.png', format='png', bbox_inches="tight")

        # # plot ROC
        # fig, ax = plt.subplots(1,1)
        # fig.suptitle('ROC curve\nstation: '+stat+'  h='+str(height)+'   spec='+spec)
        # f=np.arange(0,1,0.01)
        # i=0
        # for o in OR:
        #     h = f*o/(1+(o-1)*f)
        #     ax.plot(f,h, label = alg+' '+str(params[i]))
        #     i=i+1
        # ax.grid()
        # ax.set_xlim(0,1)
        # ax.set_ylim(0,1)
        # ax.set_aspect('equal', adjustable='box')
        # ax.legend(loc='lower right')
        # ax.set_xlabel('false alarm rate')
        # ax.set_ylabel('hit rate')
        # plt.savefig('res_plot/'+stat+'/bfor_parameters/ROC_curve_'+stat+'_'+spec+'_h'+str(height)+'_'+alg+'.pdf', format='pdf')
 
def get_standard_parameter_index(alg, params, spec):
        
        if (spec == 'CO2') or (spec =='CH4'):    
            std_params_dict = {'SD':'1.0', 'REBS':'3'}
        elif (spec == 'CO'):
            std_params_dict = {'SD':'3.0', 'REBS':'8'}
            
        param   = std_params_dict[alg]
        
        i_std = 0
        i=0
        for p in params:
            if p == param:
                i_std   = i
            i+=1
                
        return i_std
 
def get_BFOR_parameters(algorithms, stat, height, spec, inst_id, high_spikes, high_spikes_mode, quant, all_std):
    """
    Parameters
    ----------
    algorithms : list
        list with algorithm name ('SD' or 'REBS') as first element and parameters values after
    stat : str
        station name
    height : str
        sampling altitude
    spec : str
        chemical specie
    inst_id : str
        instrument ID
    high_spikes : bool
        wether to analyze high or low spikes
    high_spikes_mode : str
        see add_high_spikes_col() documentation
    quant : str
        see add_high_spikes_col() documentation
    all_std : str
        wether to return all the parameters or only the standard ones, or one given parameter. Select 'std' to get results for the standard parameters, 
        'all' to get results for all the parameters, one single parameter (e.g. '5' for REBS 5) to get results for that parameter
    Returns
    -------
    H,F,B,ORSS :
        lists with H,F,B and ORSS values for the different parameters.
    """
    
    alg = algorithms[0] # read current algorithm name (REBS or SD)
    params = algorithms[1:len(algorithms)] # get list of parameters
    B  = np.empty(0)
    H  = np.empty(0)
    F  = np.empty(0)
    OR = np.empty(0)
    ORSS = np.empty(0)
    stdev_logOR = np.empty(0)
    #min_a, min_b, min_c, min_d = 1E10,1E10,1E10,1E10
    
    if all_std == 'std': # return only results for standard parameters
        #i_std_sd, i_std_rebs = get_standard_parameter_index(alg, params, spec)
       # print(i_std_sd, i_std_rebs)
        if alg == 'SD':
            i_std_sd = get_standard_parameter_index(alg, params, spec)
            params = [str(params[i_std_sd])]
        if alg == 'REBS':
            i_std_rebs = get_standard_parameter_index(alg, params, spec)
            params = [str(params[i_std_rebs])]
        print('std params',alg, params)
    elif all_std == 'all':
        params = params
    else: # single parameter case
        params = [all_std]
        
    for param in params:
        infile_spiked = './data-minute-spiked/' + stat +'/' + fmt.get_L1_file_name(stat, height, spec, inst_id)+'_'+ alg +'_'+ param + '_spiked_PIQc_mean'
        frame = pd.read_csv(infile_spiked, sep=';')     

        if high_spikes:
           frame = add_high_spikes_col(frame, spec, high_spikes_mode, quant)
           observed = 'high_spike_'+spec.lower()+'_PIQc' # observed spikes
        else:
           observed = 'spike_'+spec.lower()+'_PIQc' # observed spikes
        
        forecast = 'spike_'+spec.lower() # forecasted spikes

        a = len(frame[ (frame[forecast]==True ) & (frame[observed]==True ) ])
        b = len(frame[ (frame[forecast]==True ) & (frame[observed]==False) ])
        c = len(frame[ (frame[forecast]==False) & (frame[observed]==True ) ])
        d = len(frame[ (frame[forecast]==False) & (frame[observed]==False) ])
        B  = np.append( B, (a+b)/(a+c))
        H  = np.append( H, a/(a+c))
        F  = np.append( F, b/(b+d))
        err=0
        if (b==0) | (c==0):
            print(alg,param,'ZERO VALUE: b=',b,'c=',c)
            OR =np.append( OR, np.nan)    
            ORSS = np.append(ORSS, np.nan)
            stdev_logOR = np.append(stdev_logOR,0)
        else:
            OR = np.append( OR, a*d/b/c)
            ORSS = np.append(ORSS, (a*d-b*c)/(a*d+b*c))
            if(a!=0) & (d!=0):
                stdev_logOR = np.append(stdev_logOR,(1/a + 1/b + 1/c + 1/d)**0.5)
            else:
                stdev_logOR = np.append(stdev_logOR,0)
                print(alg,param,'ZERO VALUE: a=',a,'d=',d)
            if (a<5) |(b<5) |(c<5) |(d<5):
                print(alg,param,'COUNT < 5:',a,b,c,d)
                OR[-1]=np.nan
                ORSS[-1]=np.nan
                err=1
        logOR=np.log(OR)    
        
        #if a < min_a:
        #    min_a=a
        #if b < min_b:
        #    min_b=b
        #if c < min_c:
        #    min_c=c
        #if d < min_d:
        #    min_d=d
        
    return H, F, B, ORSS

def BFOR_table(stations, algorithms, high_spikes, high_spikes_mode, quant): 
    config=ConfigParser()
    
    if high_spikes:
        high_suff = '_high'
    else:
        high_suff = ''
    
    
    try:
        best_frame = pd.read_csv('./tabelle_manual_flagging/table_bfor_best'+high_suff+'.txt', sep=' ', dtype=str) 
        best=True
    except:
        print('Warning: best params table not found\n')
        best=False
    
    out_table = open('./tabelle_manual_flagging/table_bfor'+high_suff+'.txt', 'w')
    out_table.write('station specie algorithm H F B')

    if not best:
        out_table.write('\n')
    if best:
        out_table.write(' best_par bH bF bB\n')
        
    for stat in stations:
        config.read('stations.ini') 
        heights = config.get(stat, 'height' ).split(',')
        species = config.get(stat, 'species').split(',')
        ID      = config.get(stat, 'inst_ID').split(',')
        ID = ID[-1]
        max_height = heights[-1] # get higher sampling altitude
        for spec in species:
            for algo in algorithms:
                H, F, B, ORSS = get_BFOR_parameters(algo, stat, max_height, spec, ID, high_spikes, high_spikes_mode, quant, all_std = 'std')
                
                if best:
                    
                    best_param = str(best_frame[(best_frame['station']==stat) & (best_frame['specie']==spec)& (best_frame['algorithm']==algo[0])]['best'].iat[0])
                    if float(best_param) < 11:
                        best_H, best_F, best_B, best_ORSS = get_BFOR_parameters(algo, stat, max_height, spec, ID, high_spikes, high_spikes_mode, quant, all_std = best_param)
                    else:
                        best_H, best_F, best_B = [999], [999], [999]
                        
                out_table.write(str(stat)+' '+str(spec)+' '+str(algo[0])+' '+str(round(H[0],2))+' '+
                                str(round(F[0],2))+' '+str(round(B[0],1)))
                if not best:
                    out_table.write('\n')
                    
                if best:
                    out_table.write(' '+str(best_param)+' '+
                                str(round(best_H[0],2))+' '+
                                str(round(best_F[0],2))+' '+
                                str(round(best_B[0],1))+'\n')
    
    out_table.close()
    
def plot_BFOR_parameters_sdrebs(stat, inst_id, algorithms, spec, height, high_spikes, high_spikes_mode, quant):
    """
    plot results from statistical analysis of PIQc and automatic flagging. Produce two plots with SD and REBS side by side
    Parameters
    ----------
    stat : str
        station name.
    inst_id : str
        instrument id.
    algorithms : 2D list
        list containing algorithms names and parameters values.
    spec : str
        specie.
    height : str
        sampling height.
    high_spikes : bool
        enable/disable analysis of "high" spikes.
    high_spikes_mode: str
        'single' or 'distr' . Choose wether to define "high" spikes according to difference of each point respect to the baseline or to the quartiles of the difference distribution
    quant: float
        quantile to evaluate the threshold for high spikes
    Returns
    -------
    None.
    """
    
    if high_spikes:
       high_spikes_str  = ' - high spikes (>'+str(min_ampl_dict[spec])+' '+fmt.get_meas_unit(spec)+')'
       high_spikes_suff = '_high'
    else:
       high_spikes_str  = ''
       high_spikes_suff = ''
    
    H, F, B, ORSS, params = [], [], [], [], [] # 2d lists with results from SD and REBS
    alg_names = []
    
    for algo in algorithms:
        h, f, b, orss = get_BFOR_parameters(algo, stat, height, spec, inst_id, high_spikes, high_spikes_mode, quant, all_std='all')
        H.append(h)
        F.append(f)
        B.append(b)
        ORSS.append(orss)
        alg_names.append(algo[0])
        params.append(algo[1:len(algo)])
        
    # # plot parameters
    fig, ax = plt.subplots(1,2, figsize=(8,5))
    plt.style.use('ggplot')
    
    fig.subplots_adjust(wspace=0.05)
   
    max_bias = max([max(b) for b in B ])
    
    for i in range(2):
        labels=[str(p) for p in params[i]]
        if len(params[i])==1: # draw points if there is only one parameter
            ax[i].scatter(params[i][0], H[i], label='hit rate', color = 'C1',marker='o')
            ax[i].scatter(params[i][0], F[i], label='false alarm rate', color = 'C1', marker='^')
            ax[i].scatter(params[i][0],H[i]-F[i], label = 'H-F', color='C1',marker='.')
            ax[i].scatter(params[i][0],ORSS[i], label = 'ORSS', color = 'C3',marker='o')
            
        ax[i].plot(H[i], label='H', color = 'C1', ls='--')
        ax[i].plot(F[i], label='F', color = 'C1', ls=':')
        ax[i].plot(H[i]-F[i], label = 'PSS', color='C1')
        ax[i].plot(ORSS[i], label = 'ORSS', color = 'C3')
    
        ax[i].set_xticks(np.arange(0,len(params[i]),1))
        ax[i].set_xticklabels(labels)
        ax[i].set_yticks(np.arange(0,1.1,0.1))
        #ax[i].set_yticklabels(str l for l in np.arange())
        # t=ax.text(1.3,  0.2, 'min a= '+str(min_a)+'\nmin b= '+str(min_b)+'\nmin c= '+str(min_c)+'\nmin d= '+str(min_d), horizontalalignment='center', size='large', color='black',transform=ax.transAxes)                                              
        # t.set_bbox(dict(facecolor='grey', alpha=0.3))
        ax[i].set_xlabel(alg_names[i])
        ax[i].set_ylim(0,1.05)
        if (min(ORSS[i])<0) & (min(ORSS[i])>-100):
            ax[i].set_ylim(min(ORSS[i])-0.1,1.05)
    
        if spec=='CO':
            if alg_names[0]=='REBS':
                ax[i].axvline(7,c='black',ls=':')  
            elif alg_names[0]=='SD':
                ax[i].axvline(6,c='black',ls=':')
        else:
            if alg_names[0]=='REBS':
                ax[i].axvline(2,c='black',ls=':')  
            elif alg_names[0]=='SD':
                ax[i].axvline(2,c='black',ls=':')
        
        ax2 = ax[i].twinx()
        ax2.plot(B[i], label = 'BIAS', color = 'C2')
        #ax2.errorbar(np.arange(0,len(logOR),1), logOR, stdev_logOR,elinewidth=1, capsize =5, ls='none', fmt="o", color = 'C2', label = 'log OR')
        ax2.axhline(1, c='C2',ls=':',lw=3)
        ax2.tick_params('y',which='both', colors='C2')
        ax2.grid(visible=False)
        if max_bias>1.5:
            ax2.set_ylim(0, max_bias*1.05)        
        else:
            ax2.set_ylim(0, 1.5)
        
        if i ==0:
            ax2.tick_params(axis='y', right=False, labelright=False)
        
        if i>0: # legend only on second plot
            ax2.legend(  loc=[1.15,0.6])
            ax[i].legend(loc=[1.15,0.7])
            ax[i].tick_params(axis='y', left=False, labelleft=False)
        if max_bias>10:
            ax2.set_ylim(0.1,max_bias*1.05)
            ax2.set_yscale('log')
        ax[i].grid(visible=True)
    # write infos on spike percentage
    #stat_text = 'PIQc spikes = '+str(round((a+c)/(a+b+c+d)*100,2))+'%'
    #t1=ax.text(1.05,  0.05, stat_text, horizontalalignment='left', size='large', color='black',transform=ax.transAxes)
    #t1.set_bbox(dict(facecolor='tan', alpha=0.3))
    fig.suptitle('Statistical parameters\nstation: '+stat+'  h='+str(height)+'   spec='+spec+high_spikes_str)
    fig.tight_layout()
    plt.savefig('res_plot/'+stat+'/bfor_parameters/bfor_parameters_sdrebs_'+stat+'_'+spec+'_h'+str(height)+'_'+algo[0]+high_spikes_suff+'.png', format='png', bbox_inches="tight")


def plot_BFOR_parameters_lowhigh(stat, inst_id, algorithms, spec, height,  high_spikes_mode, quant):
    """
    plot results from statistical analysis of PIQc and automatic flagging. Produce two plots with results from low and high spikes analysis
    Parameters
    ----------
    stat : str
        station name.
    inst_id : str
        instrument id.
    algorithms : 2D list
        list containing algorithms names and parameters values.
    spec : str
        specie.
    height : str
        sampling height.
    high_spikes : bool
        enable/disable analysis of "high" spikes.
    high_spikes_mode: str
        'single' or 'distr' . Choose wether to define "high" spikes according to difference of each point respect to the baseline or to the quartiles of the difference distribution
    quant: float
        quantile to evaluate the threshold for high spikes
    Returns
    -------
    None.
    """
    
    high_spikes_str  = ' - low and high spikes (>'+str(min_ampl_dict[spec])+' '+fmt.get_meas_unit(spec)+')'
  
    H, F, B, ORSS, params = [], [], [], [], [] # 2d lists with results from SD and REBS
    alg_names = []
    
    for algo in algorithms: # a list of four lists for each H,F,B and ORSS is created. The first two lists correspond to results from the first algorithm, the 3rd and the 4th o the second algorithm
        for high_spikes in [False, True]: # get results from low and high spikes flagging
            h, f, b, orss = get_BFOR_parameters(algo, stat, height, spec, inst_id, high_spikes, high_spikes_mode, quant, all_std='all')
            H.append(h)
            F.append(f)
            B.append(b)
            ORSS.append(orss)
            alg_names.append(algo[0])
            params.append(algo[1:len(algo)])
    
    for k in [0,2]:
        # # plot parameters
        fig, ax = plt.subplots(1,2, figsize=(8,5))
        plt.style.use('ggplot')
        
        fig.subplots_adjust(wspace=0.05)
       
        max_bias = max([max(b) for b in B[k:k+2] ])
        for i in range(2):
            
            if len(params[k+i])==1:  # draw points if there is only one parameter
                ax[i].scatter(params[k+i][0],H[k+i], label='H', color = 'C1', marker='o')
                ax[i].scatter(params[k+i][0],F[k+i], label='F', color = 'C1', marker='^')
                ax[i].scatter(params[k+i][0],H[k+i]-F[k+i], label = 'PSS', color='C1',marker='.')
                ax[i].scatter(params[k+i][0],ORSS[k+i], label = 'ORSS', color = 'C3',marker='o') 
            
            else:
                ax[i].plot(H[k+i], label='H', color = 'C1', ls='--')
                ax[i].plot(F[k+i], label='F', color = 'C1', ls=':')
                ax[i].plot(H[k+i]-F[k+i], label = 'PSS', color='C1')
                ax[i].plot(ORSS[k+i], label = 'ORSS', color = 'C3')
            
            labels=[str(p) for p in params[k+i]]

            ax[i].set_xticks(np.arange(0,len(params[k+i]),1))
            ax[i].set_xticklabels(labels)
            ax[i].set_yticks(np.arange(0,1.1,0.1))
            #ax[i].set_yticklabels(str l for l in np.arange())
            # t=ax.text(1.3,  0.2, 'min a= '+str(min_a)+'\nmin b= '+str(min_b)+'\nmin c= '+str(min_c)+'\nmin d= '+str(min_d), horizontalalignment='center', size='large', color='black',transform=ax.transAxes)                                              
            # t.set_bbox(dict(facecolor='grey', alpha=0.3))
            ax[i].set_xlabel(alg_names[k+i])
            ax[i].set_ylim(0,1.05)
            if (min(ORSS[k+i])<0) & (min(ORSS[k+i])>-100):
                ax[i].set_ylim(min(ORSS[k+i])-0.1,1.05)
        
            if spec=='CO':
                if alg_names[0]=='REBS':
                    ax[i].axvline(7,c='black',ls=':')  
                elif alg_names[0]=='SD':
                    ax[i].axvline(6,c='black',ls=':')
            else:
                if alg_names[0]=='REBS':
                    ax[i].axvline(2,c='black',ls=':')  
                elif alg_names[0]=='SD':
                    ax[i].axvline(2,c='black',ls=':')
            
            ax2 = ax[i].twinx()
            if len(params[k+i])==1:  # draw points if there is only one parameter
                ax2.scatter(params[k+i][0] ,B[k+i], label = 'BIAS', color = 'C2')
            else:
                ax2.plot(B[k+i], label = 'BIAS', color = 'C2')
            #ax2.errorbar(np.arange(0,len(logOR),1), logOR, stdev_logOR,elinewidth=1, capsize =5, ls='none', fmt="o", color = 'C2', label = 'log OR')
            ax2.axhline(1, c='C2',ls=':',lw=3)
            ax2.tick_params('y',which='both', colors='C2')
            ax2.grid(visible=False)
            if max_bias>1.5:
                ax2.set_ylim(0, max_bias*1.05)        
            else:
                ax2.set_ylim(0, 1.5)
            
            if i ==0:
                ax2.tick_params(axis='y', right=False, labelright=False)
            
            if i>0: # legend only on second plot
                ax2.legend(  loc=[1.15,0.6])
                ax[i].legend(loc=[1.15,0.7])
                ax[i].tick_params(axis='y', left=False, labelleft=False)
            if max_bias>10:
                ax2.set_ylim(0.1,max_bias*1.05)
                ax2.set_yscale('log')
            ax[i].grid(visible=True)
        # write infos on spike percentage
        #stat_text = 'PIQc spikes = '+str(round((a+c)/(a+b+c+d)*100,2))+'%'
        #t1=ax.text(1.05,  0.05, stat_text, horizontalalignment='left', size='large', color='black',transform=ax.transAxes)
        #t1.set_bbox(dict(facecolor='tan', alpha=0.3))
        fig.suptitle('Statistical parameters\nstation: '+stat+'  h='+str(height)+'   spec='+spec+high_spikes_str)
        fig.tight_layout()
        plt.savefig('res_plot/'+stat+'/bfor_parameters/bfor_parameters_lowhigh_'+stat+'_'+spec+'_h'+str(height)+'_'+alg_names[k]+'.png', format='png', bbox_inches="tight")


    
def get_threshold(df, spec, mode, quant):
    if mode =='single':
        min_diff = min_ampl_dict[spec.upper()] 
    elif mode =='distr':
        min_diff = df[df['spike_'+spec.lower()+'_PIQc']]['spike_amplitude_'+spec.lower()+'_PIQc'].quantile(q=quant) # set the quantile as min difference
    else:
        print('unknown high_spikes_mode')        
    return min_diff

def add_high_spikes_col(df, spec, mode, quant):
    df.insert(len(df.columns),'high_spike_'+spec.lower()+'_PIQc',False)
    min_diff = get_threshold(df, spec, mode, quant)
    df.loc[df['spike_amplitude_'+spec.lower()+'_PIQc'] > min_diff, 'high_spike_'+spec.lower()+'_PIQc'] = True
    return df
    
def qqplot(x, y, height,    quantiles=None, interpolation='nearest', ax=None, rug=False, rug_length=0.05, rug_kwargs=None,  **kwargs):
    """Draw a quantile-quantile plot for `x` versus `y`.

    Parameters
    ----------
    x, y : array-like
        One-dimensional numeric arrays.

    ax : matplotlib.axes.Axes, optional
        Axes on which to plot. If not provided, the current axes will be used.

    quantiles : int or array-like, optional
        Quantiles to include in the plot. This can be an array of quantiles, in
        which case only the specified quantiles of `x` and `y` will be plotted.
        If this is an int `n`, then the quantiles will be `n` evenly spaced
        points between 0 and 1. If this is None, then `min(len(x), len(y))`
        evenly spaced quantiles between 0 and 1 will be computed.

    interpolation : {‘linear’, ‘lower’, ‘higher’, ‘midpoint’, ‘nearest’}
        Specify the interpolation method used to find quantiles when `quantiles`
        is an int or None. See the documentation for numpy.quantile().

    rug : bool, optional
        If True, draw a rug plot representing both samples on the horizontal and
        vertical axes. If False, no rug plot is drawn.

    rug_length : float in [0, 1], optional
        Specifies the length of the rug plot lines as a fraction of the total
        vertical or horizontal length.

    rug_kwargs : dict of keyword arguments
        Keyword arguments to pass to matplotlib.axes.Axes.axvline() and
        matplotlib.axes.Axes.axhline() when drawing rug plots.

    kwargs : dict of keyword arguments
        Keyword arguments to pass to matplotlib.axes.Axes.scatter() when drawing
        the q-q plot.
    """
    # Get current axes if none are provided
    if ax is None:
        ax = plt.gca()

    if quantiles is None:
        quantiles = min(len(x), len(y))

    # Compute quantiles of the two samples
    if isinstance(quantiles, numbers.Integral):
        quantiles = np.linspace(start=0, stop=1, num=int(quantiles))
    else:
        quantiles = np.atleast_1d(np.sort(quantiles))
    x_quantiles = np.quantile(x, quantiles, interpolation=interpolation)
    y_quantiles = np.quantile(y, quantiles, interpolation=interpolation)

    # Draw the rug plots if requested
    if rug:
        # Default rug plot settings
        rug_x_params = dict(ymin=0, ymax=rug_length, c='gray', alpha=0.5)
        rug_y_params = dict(xmin=0, xmax=rug_length, c='gray', alpha=0.5)

        # Override default setting by any user-specified settings
        if rug_kwargs is not None:
            rug_x_params.update(rug_kwargs)
            rug_y_params.update(rug_kwargs)

        # Draw the rug plots
        for point in x:
            ax.axvline(point, **rug_x_params)
        for point in y:
            ax.axhline(point, **rug_y_params)
    
    # Draw the q-q plot
    ax.scatter(x_quantiles, y_quantiles, c='red', s=13, alpha=0.5, edgecolor='k')
    
    # Format axes
    ax.grid()
    ax.set_aspect('equal', 'datalim')
    t=ax.text(0.5,  0.9, height+' m', horizontalalignment='center', size='large', color='black',transform=ax.transAxes)                                              
    t.set_bbox(dict(facecolor='grey', alpha=0.3))
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
