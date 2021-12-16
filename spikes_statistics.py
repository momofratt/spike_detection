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

def plot_BFOR_parameters(stat, inst_id, algorithms, spec, height):
    
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
            infile_spiked = './data-minute-spiked/' + stat +'/' + fmt.get_L1_file_name(stat, height, spec, inst_id)+'_'+ alg +'_'+ param + '_spiked_PIQc'
            frame = pd.read_csv(infile_spiked, sep=';')
            forecast = 'spike_'+spec.lower()
            observed = 'spike_'+spec.lower()+'_PIQc'
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
        fig.suptitle('Statistical parameters\nstation: '+stat+'  h='+str(height)+'   spec='+spec)
        labels=[str(p) for p in params]
        ax.plot(H, label='hit rate', color = 'C1', ls='--')
        ax.plot(F, label='false alarm rate', color = 'C1', ls=':')
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
        plt.savefig('res_plot/'+stat+'/bfor_parameters/bfor_parameters_'+stat+'_'+spec+'_h'+str(height)+'_'+alg+'.pdf', format='pdf', bbox_inches="tight")
        
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
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    