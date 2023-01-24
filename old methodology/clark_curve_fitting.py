"""
This module contains functions for fitting the Clark curve to a given dataset.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sb
import numdifftools as nd

from scipy.optimize import minimize


def split_data(x, train=0.6, validate=0.2, test=0.2):
    """
    # Description:
        This function splits a dataset into train, validate, and test sets.
    # Inputs:
        x: a pandas dataframe
        train: the proportion of the data to be used for training
        validate: the proportion of the data to be used for validation
        test: the proportion of the data to be used for testing
    # Outputs:
        out: a string indicating which set the row belongs to
    # Example:
        df['set'] = df.apply(lambda x: split_data(x, train=0.6, validate=0.2, test=0.2), axis=1)
    """
    # normalize the proportions
    d = (train + validate + test)
    train1, validate1, test1= train/d, validate/d, test/d

    # assign the set:
    # train if x is less than or equal to the train proportion 
    if x<=train1:
        out='train'

    # validate if x is less than or equal to the train + validate proportion and greater than the train proportion
    elif (x<=train1 + validate1) and (x>train1):
        out='validate'

    # test if x is greater than the train + validate proportion
    else:
        out='test'

    # return the set
    return(out)
    
def cross_validation_label_func(x, n_labels=5):
    """
    # Description:
        This function splits a dataset into n_labels sets for cross validation.
    # Inputs:
        x: a pandas dataframe
        n_labels: the number of labels to create
                  default is 5
    # Outputs:      
        out: a string indicating which set the row belongs to
    # Example:
        df['set'] = df.apply(lambda x: cross_validation_label_func(x, n_labels=5), axis=1)
    """
    # create a dataframe with the labels
    df = pd.DataFrame(dict(gp=range(1, n_labels+1)))

    # create the min and max values for each label:
    df['min'] = [i / n_labels for i in range(n_labels)]
    df['max'] = [min(i+1, n_labels) / n_labels for i in range(n_labels)]
    
    # assign the label
    # replicate this code for each label, but avoid using a for loop:
    # for i in range(n_labels):
    #     if (x > df['min'][i]) and (x <= df['max'][i]):
    #         out = df['gp'][i]

    # assign the label
    out = df.apply(lambda x: x['gp'] if (x['min'] < x['gp'] <= x['max']) else None, axis=1)
    out = out[out.notnull()].values[0]

    # return the label
    return(out)
    



## 1. Functions for model fit
def G(age, theta, curve_type='loglogistic'):
    '''
    # Description:
        This function returns the percent of ultimate paid, given parameter vector `theta`
        `theta[0]` is omega/warp in the model above
        `theta[1]` is theta in the model above
    # Inputs:
        age: the age of the claim
        theta: a vector of parameters
        curve_type: the type of curve to fit
                    default is 'loglogistic'
    # Outputs:
        out: the percent of ultimate paid
    # Example:
        >>> G(age=1, theta=[1, 1], curve_type='loglogistic')
        0.6321205588285577
    '''

    # check the curve type
    if curve_type=='weibull':
        out = 1-np.exp(-np.power((np.divide(age, theta[1])),theta[0]))
    elif curve_type=='exponential':
        out = 1-np.exp(-age/theta[0])
    else:
        out = np.power(age, theta[0]) / (np.power(age, theta[0]) + np.power(theta[1],theta[0]))
    return(out)

def Ult_ldf(origin, age, paid, theta, curve_type='loglogistic'):
    """
    # Description:
        This function returns the ultimate loss development factor, given parameter vector `theta`
        `theta[0]` is omega/warp in the model above
        `theta[1]` is theta in the model above
    # Inputs:
        origin: the origin year of the claim
        age: the age of the claim
        paid: the paid amount of the claim
        theta: a vector of parameters
        curve_type: the type of curve to fit
                    default is 'loglogistic'
    # Outputs:
        out: the ultimate loss development factor
    # Example:
        >>> Ult_ldf(origin=2010, age=1, paid=100, theta=[1, 1], curve_type='loglogistic')
        0.6321205588285577
    """
    # create a dataframe
    df = pd.DataFrame(dict(ay=origin, age=age, paid=paid))

    # calculate the percent of ultimate paid for each age
    df['G'] = df.age.apply(lambda x: G(x, theta=theta, curve_type=curve_type))

    # calculate the percent of ultimate paid for each age - 1
    df['G1'] = df.age.apply(lambda x: 0 if x==12 else G(x-12, theta=theta, curve_type=curve_type))

    # calculate the ultimate loss development factor
    df['ult1'] = df.paid / (df.G - df.G1)

    # sum the ultimate loss development factor by origin year
    ult_df = (df[['ay'] + ['ult1']]
                .groupby('ay')
                .sum()
                .reset_index()
                .rename(columns=dict(ult1='ult'))
            )

    # merge the ultimate loss development factor back to the original dataframe
    df = df.merge(ult_df, how='left', on='ay')

    # calculate the ultimate loss development factor
    return(df.ult)

def mu_ldf(origin, age, paid, theta, ult=None, curve_type='loglogistic'):
    """
    # Description:
        This function returns the expected loss development factor, given parameter vector `theta`
        `theta[0]` is omega/warp in the model above
        `theta[1]` is theta in the model above
    # Inputs:
    
    """
    if ult is None:
        ult1 = Ult_ldf(origin=origin, age=age, paid=paid, theta=theta, curve_type=curve_type)
    else:
        ult1 = ult
        
    df = pd.DataFrame(dict(ay=origin, age=age, paid=paid, ult=ult1))
    df['G'] = df.age.apply(lambda x: G(age=x, theta=theta, curve_type=curve_type))
    df["G2"] = df.age.apply(lambda x: 0 if x==12 else G(age=x-12, theta=theta, curve_type=curve_type))
        
    df['mu'] = df.ult * (df.G - df.G2)
    return(df.mu)

def loglik_ldf(origin, age, paid, theta, ult=None, curve_type='loglogistic'):
    '''return the loglikelihood term'''
    if ult is None:
        ult1 = Ult_ldf(origin=origin, age=age, paid=paid, theta=theta, curve_type=curve_type)
    else:
        ult1 = ult
    m = mu_ldf(origin=origin, age=age, paid=paid, theta=theta, ult=ult1, curve_type=curve_type)
    out = paid * np.log(m) - m
    return(out)
    
def elr_cc(origin, age, paid, prem, theta, curve_type='loglogistic'):
    ## get df/define G
    df = pd.DataFrame(dict(ay=origin, age=age, c=paid, p=prem)).query('age > 0')
    df['G'] = G(age=df.age, theta=theta, curve_type=curve_type)

    ## figure out what the lag is
    x = df.age.sort_values().unique()
    lagdf = pd.DataFrame(dict(age=x, age1=pd.Series(x).shift().fillna(0).astype(int)))
    lagdf['diff'] = lagdf.age - lagdf.age1
    df_lag = lagdf['diff'].min()

    ## define G1/G_inc
    df['G1'] = G(age=df.age.apply(lambda x: 0 if x==0 else x-df_lag), theta=theta, curve_type=curve_type)
    df['G_inc'] = df['G'] - df['G1']

    ## ELR = sum(c) / sum(Prem * [G - G1])
    elr = df.c.sum() / (df.p * df.G_inc).sum()

    return(elr)
    
def ult_cc(origin, age, paid, prem, theta, curve_type='loglogistic', fixed_elr=None):
    ## get df/define G
    df = pd.DataFrame(dict(ay=origin, age=age, c=paid, p=prem)).query('age > 0')
    if fixed_elr is None:
        elr = elr_cc(origin=origin, age=age, paid=paid, prem=prem, theta=theta, curve_type=curve_type)
    else:
        elr = fixed_elr
    df['ult'] = df.p * elr
    
    return(df.ult)
    
def mu_cc(origin, age, paid, prem, theta, curve_type='loglogistic', fixed_elr=None):
    ## get df/define G
    df = pd.DataFrame(dict(ay=origin, age=age, c=paid, p=prem)).query('age > 0')
    df['G'] = G(age=df.age, theta=theta, curve_type=curve_type)
    
    ## figure out what the lag is
    x = df.age.sort_values().unique()
    lagdf = pd.DataFrame(dict(age=x, age1=pd.Series(x).shift().fillna(0).astype(int)))
    lagdf['diff'] = lagdf.age - lagdf.age1
    df_lag = lagdf['diff'].min()
    # print('df_lag: {}'.format(df_lag))
    
    ## define G1/G_inc
    df['G1'] = G(age=df.age.apply(lambda x: 0 if x==0 else x-df_lag), theta=theta, curve_type=curve_type)
    df['G_inc'] = df['G'] - df['G1']
    
    ## get ult
    df['ult'] = ult_cc(origin=origin, age=age, paid=paid, prem=prem, theta=theta, curve_type=curve_type, fixed_elr=fixed_elr)
    
    ## finish with mu
    df['mu'] = df.ult * df.G_inc
    return(df.mu)  


def loglik_cc(origin, age, paid, prem, theta, curve_type='loglogistic', fixed_elr=None):
    ## loglik term = c * ln(mu) - mu
    
    ## get df
    df = pd.DataFrame(dict(ay=origin, age=age, c=paid, p=prem)).query('age > 0')
    
    ## get mu
    df['mu'] = mu_cc(origin=origin, age=age, paid=paid, prem=prem, theta=theta, curve_type=curve_type, fixed_elr=fixed_elr)
    
    ## loglikelihood term
    df['loglik'] = df.c * df.mu.apply(lambda x: np.log(x)) - df.mu
    
    return(df.loglik)
    
def mle_opt_function_cc(origin, age, paid, prem, theta, curve_type='loglogistic', fixed_elr=None):
    ## get df
    df = loglik_cc(origin=origin, age=age, paid=paid, prem=prem, theta=theta, curve_type=curve_type, fixed_elr=fixed_elr)
    s = df.sum()
    out = s*(-1)
    return(out)
    
def resid_plot(df, column, ax, col_title=None, x_string=True, plot_mean=True, plot_zero=True, logscale=False, ylim=None, x_rotate=None, alpha=0.3, sp_linecolor='black', sp_linewidths=1, zero_linewidth=0.5, point_hue=None):
    '''produces a residual plot, where normalized residuals are grouped by `column` parameter
    --------------------------------------------------------------------------------------
    
    parameters:
    ----------
    - `df` -- dataframe, has columns named "normalized_resid" and the `column` parameter
    - `column` -- string, name of a (usually categorical) column in `df` that will be the x-axis of the plot
    - `ax` -- matplotlib axis defined
    - `col_title` -- string, defaults to `column`, otherwise is the title of the chart
    - `x_string` -- boolean, defaults to `True`, should the x-axis be considered a category rather than a numeric value?
    - `plot_mean` -- boolean, defaults to `True`, should the mean residual and +/- 1 SD be plotted alongside the residuals?
    - `plot_zero` -- boolean, defaults to `True`, should the y=0 line be plotted alongside everything else (for clarity)?
    - `logscale` -- boolean, defaults to `False`, if x is a numeric variable, should it be plotted on a log-scale rather than actual-scale (to remove influence of outliers)
    - `ylim` -- [minimum, maximum], defaults to `None`, if included, will set the window limits for the y-axis, for example if there is an outlier making it tough to see everything else
    - `x_rotate` -- float in (0, 360), defaults to `None`, if included, will rotate the x-axis tick labels to make them fit better
    - `alpha` -- float in (0, 1), defaults to 0.3, controls how transparent the scatterplot points are
    - `sp_linecolor` -- string, defaults to "black", controls the color of the border drawn around the scatterplot points to make them more visible
    - `sp_linewidths` -- float, defaults to 1.0, controls the width of the edges drawn around scatterplot points to make them more visible
    - `zero_linewidth` -- float, defaults to 0.5, controls the width of the zero line
    - `point_hue` -- string, defaults to `None`, column name that controls the hue of the points
    '''
    
    # if axis is None:
        # fig, ax  = plt.subplots()
    # else:
        # ax = axis
        
    if col_title is None:
        col_title = 'Normalized Residuals by {}'.format(column)
        
    if ylim is None:
        pass
    else:
        col_title = col_title + ', y-axis scaled down to {}'.format(ylim)
    
    ## 
    logtitle = ''
    
    if point_hue is None:
        df1 = df['normalized_resid {}'.format(column).split()].copy().sort_values(column)
    else:
        df1 = df[[point_hue]+'normalized_resid {}'.format(column).split()].copy().sort_values(column)
    
    if x_string:
        df1['dm'] = df1.loc[:, column].copy().astype(str)
    else:
        df1['dm'] = df1.loc[:, column].copy()
    
    ## handles the alpha (transparency) parameter    
    if alpha is None:
        alpha1=1
    else:
        alpha1=alpha

    ## plot the scatterplot
    # if linecolor is None:
        # df1.plot(kind='scatter', x='dm', y='normalized_resid', title='Normalized Residuals by {}'.format(col_title), ax=ax, xlabel=col_title, ylabel='Normalized Residual', alpha=alpha1)
    # else:
    if logscale:
        # df1['normalized_resid'] = np.log(df1['normalized_resid'])
        df1['dm'] = np.log(df1['dm'])
        logtitle = ' (Log-Scale)'
    else:
        logtitle = ''
        
    ## calculate mean
    mean_df = df1.groupby('dm').agg('mean std'.split()).reset_index().sort_values('dm')
    mean_df['mean_resid'], mean_df['std_resid'] = mean_df['normalized_resid']['mean'], mean_df['normalized_resid']['std']
    mean_df.drop('normalized_resid', 1, level=0, inplace=True)
    mean_df['zero line'] = 0
    agdf = mean_df.copy()
    
    # calculate SD
    # sd_df = df1.groupby('dm').std().rename(columns=dict(normalized_resid='std_resid')).sort_values('dm')

    # if column in mean_df.columns.tolist():
        # mean_df.drop(column, 1, inplace=True)
    # if column in sd_df.columns.tolist():
        # sd_df.drop(column, 1, inplace=True)
        
    # join SD to mean df
    # agdf = mean_df.join(sd_df, how='left').reset_index()
    
    # mean + SD && mean - SD columns
    agdf['plus1'] = agdf.mean_resid + agdf.std_resid
    agdf['minus1'] = agdf.mean_resid - agdf.std_resid
    
    ## sort values before plotting
    agdf = agdf.assign(dm1=agdf.dm.astype(int)).sort_values('dm1')
    
    ## if includes the mean plot, calculate mean, then plot it
    if plot_mean:
    
        # plot the mean
        agdf.plot(kind='line', x='dm', y='mean_resid', ax=ax, label='Mean Residual'+logtitle, ls='-')
        
        ## plot +/-1 SD lines
        agdf.plot(kind='line', x='dm', y='plus1', ax=ax, label='Mean+1SD'+logtitle, ls='--')
        agdf.plot(kind='line', x='dm', y='minus1', ax=ax, label='Mean-1SD'+logtitle, ls='--')
    
    # plot the zero line
    agdf.plot(kind='line', x='dm', y='zero line', ax=ax, label='Zero', ls='-', color='black', linewidth=zero_linewidth, title='Normalized Residuals by {}{}'.format(col_title, logtitle))
        
       
    ## either splits by col passed with `point_hue` parameter or doesn't
    if point_hue is None:
        df1.plot(kind='scatter', 
                 x='dm', 
                 y='normalized_resid', 
                 title='Normalized Residuals by {}{}'.format(col_title, logtitle), 
                 ax=ax, 
                 # xlabel=col_title+logtitle, 
                 # ylabel='Normalized Residuals', 
                 alpha=alpha1, 
                 edgecolors=sp_linecolor, 
                 linewidths=sp_linewidths)
                 
    else:
        df1[point_hue] = df1[point_hue].astype('category')
        sb.scatterplot(
            x='dm', 
            y='normalized_resid', 
            data=df1,
            hue=point_hue,
            hue_order=df1[point_hue].drop_duplicates().sort_values().to_numpy(), 
            ax=ax, 
            alpha=alpha1, 
            edgecolors=sp_linecolor, 
            linewidths=sp_linewidths
            )
        # ax.title('Normalized Residuals by {}{}'.format(col_title, logtitle))
        ax.set_xlabel(col_title+logtitle)
        ax.set_ylabel('Normalized Residuals') 

    ## if you pass a `ylim` parameter, will scale the window    
    if ylim is None:
        pass
    else:
        ax.set_ylim(ylim)

    ## title for the plot
    ax.set_xlabel(col_title+logtitle)
    
    ## rotate the x-axis labels
    if x_rotate is None:
        pass
    else:
        plt.xticks (rotation=x_rotate) 
    plt.show()
    
    
    
## partial derivatives for loglogistic curve
def ll_all_pder(x, theta):
    warp=theta[0]
    theta0=theta[1]
    xwarp = np.power(x, warp)
    thetawarp = theta0^warp
    xwarp_thetawarp = xwarp + thetawarp
    out = (warp, theta0, xwarp, thetawarp, xwarp_thetawarp)
    return(out)

def ll_pder_G_warp(x, theta):
    num = np.multiply(np.multiply(np.power(x,theta[0]), np.power(theta[1],theta[0])), np.log(np.divide(x, theta[1])))
    den = np.power(np.power(x,theta[0]) + np.power(theta[1],theta[0]), 2)
    out = np.divide(num, den)
    return(out)

def ll_pder_G_theta(x, theta):
    num = np.multiply(np.multiply(np.power(x, theta[0]), np.power(theta[1],theta[0])), (-theta[0]))
    den = np.multiply(np.power(np.power(x,theta[0]) + np.power(theta[1],theta[0]), 2), theta[1])
    out = np.divide(num, den)
    return(out)

def ll_pder2_G_warp2(x, theta):
    xwarp = np.power(x, theta[0])
    thetawarp = np.power(theta[1],theta[0])
    
    num = np.multiply(
        np.multiply(
            np.multiply(xwarp,thetawarp),
            np.power(np.log(np.divide(x, theta[1])), 2)
        ), 
        (1 - 2*np.divide(xwarp, xwarp + thetawarp))
    )
    den = np.power(xwarp + thetawarp, 2)
    out = np.divide(num, den)
    return(out)

def ll_pder2_G_warptheta(x, theta):
    warp=theta[0]
    theta0=theta[1]
    
    xwarp = np.power(x, warp)
    thetawarp = np.power(theta[1],theta[0])
    xwarp_thetawarp = xwarp + thetawarp
    
    fct1 = np.divide(xwarp, xwarp_thetawarp)
    fct2 = np.divide(thetawarp, xwarp_thetawarp)
    fct3 = (-1/theta0)
    
    fct4a = 1 - np.multiply(2,(np.divide(xwarp, xwarp_thetawarp)))
    fct4b = np.log(np.divide(x, theta0))
    fct4 = 1 + np.multiply(warp, np.multiply(fct4a, fct4b))
    
    out = np.multiply(np.multiply(np.multiply(fct1, fct2), fct3), fct4)
    return(out)

def ll_pder2_G_theta2(x, theta):
    warp, theta0, xwarp, thetawarp, xwarp_thetawarp = ll_all_pder(x=x, theta=theta)
    
    fct1 = np.divide(xwarp, xwarp_thetawarp)
    fct2 = np.divide(thetawarp, xwarp_thetawarp)
    fct3 = np.divide(warp, (np.power(theta0,2)))
    
    fct4a = np.subtract(1, np.multiply(2,(np.divide(xwarp, xwarp_thetawarp))))
    fct4 = 1 + np.multiply(warp,fct4a)
    out = np.multiply(np.multiply(np.multiply(fct1, fct2), fct3), fct4)
    return(out)  
    
## partial derivatives for loglikelihood
def ll_pder2_elr2(c, elr):
    num = (-c).sum()
    den = np.power(elr, 2)
    out = np.divide(num, den)
    return(out)

def ll_pder2_elr_warp(prem, age, theta, age_diff):
    g1 = ll_pder_G_warp(x=age, theta=theta)
    g2 = ll_pder_G_warp(x=age - age_diff, theta=theta)
    series = np.multiply(prem, np.subtract(g1, g2))
    out = -series.sum()
    return(out)

def ll_pder2_elr_theta(prem, age, theta, age_diff):
    g1 = ll_pder_G_theta(x=age, theta=theta)
    g2 = ll_pder_G_theta(x=age - age_diff, theta=theta)
    series = np.multiply(prem, np.subtract(g1, g2))
    out = -series.sum()
    return(out)

def ll_pder2_warp2(c, prem, age, theta, elr, age_diff):
    g1 = ll_pder_G_warp(x=age, theta=theta)
    g2 = ll_pder_G_warp(x=age - age_diff, theta=theta)
    g1_2 = np.subtract(g1, g2)
    
    g1_2 = ll_pder2_G_warp2(x=age, theta=theta)
    g2_2 = ll_pder2_G_warp2(x=age - age_diff, theta=theta)
    
    G1 = G(age=age, theta=theta, curve_type='loglogistic')
    G2 = G(age=age - age_diff, theta=theta, curve_type='loglogistic')
    G1_2 = np.subtract(G1, G2)
    
    fct1a = np.multiply((-1), np.divide(c, np.power(G1_2, 2)))
    fct1b = np.power(g1_2, 2)
    fct1 = np.multiply(fct1a, fct1b)
    
    fct2a = np.subtract(np.divide(c, G1_2), np.multiply(prem, elr))
    fct2b = g1_2
    fct2 = np.multiply(fct2a, fct2b)
    
    series = pd.Series(fct1) + pd.Series(fct2)
    out = series.sum()
    return(out)

def ll_pder2_theta2(c, prem, age, theta, elr, age_diff):
    g1 = ll_pder_G_theta(x=age, theta=theta)
    g2 = ll_pder_G_theta(x=age - age_diff, theta=theta)
    g1_2 = np.subtract(g1, g2)
    
    g1_2 = ll_pder2_G_theta2(x=age, theta=theta)
    g2_2 = ll_pder2_G_theta2(x=age - age_diff, theta=theta)
    
    G1 = G(age=age, theta=theta, curve_type='loglogistic')
    G2 = G(age=age - age_diff, theta=theta, curve_type='loglogistic')
    G1_2 = np.subtract(G1, G2)
    
    fct1a = np.multiply((-1), np.divide(c, np.power(G1_2, 2)))
    fct1b = np.power(g1_2, 2)
    fct1 = np.multiply(fct1a, fct1b)
    
    fct2a = np.subtract(np.divide(c, G1_2), np.multiply(prem, elr))
    fct2b = np.subtract(g1_2)
    fct2 = np.multiply(fct2a, fct2b)
    
    series = pd.Series(fct1) + pd.Series(fct2)
    out = series.sum()
    return(out)

def ll_pder2_theta_warp(c, prem, age, theta, elr, age_diff):
    g1_theta = ll_pder_G_theta(x=age, theta=theta)
    g2_theta = ll_pder_G_theta(x=age - age_diff, theta=theta)
    g1_2_theta = np.subtract(g1_theta, g2_theta)
    
    g1_warp = ll_pder_G_warp(x=age, theta=theta)
    g2_warp = ll_pder_G_warp(x=age - age_diff, theta=theta)
    g1_2_warp = np.subtract(g1_warp, g2_warp)
    
    g1_thetawarp = ll_pder2_G_warptheta(x=age, theta=theta)
    g2_thetawarp = ll_pder2_G_warptheta(x=age - age_diff, theta=theta)
    g1_2_thetawarp = np.subtract(g1_thetawarp, g2_thetawarp)
    
    G1 = G(age=age, theta=theta, curve_type='loglogistic')
    G2 = G(age=age - age_diff, theta=theta, curve_type='loglogistic')
    G1_2 = np.subtract(G1, G2)
    
    fct1a = np.divide(-c, np.power(G1_2, 2))
    fct1b = g1_2_warp
    fct1c = g1_2_theta
    fct1 = np.multiply(np.multiply(fct1a, fct1b), fct1c)
    
    fct2a = np.subtract(np.divide(c, G1_2), np.multiply(prem, elr))
    fct2b = g1_2_thetawarp
    fct2 = np.multiply(fct2a, fct2b)
    
    series = pd.Series(fct1) + pd.Series(fct2)
    return(series.sum())

def ll_info_matrix(origin, c, prem, age, theta, age_diff):
    elr = elr_cc(origin=origin, age=age, paid=c, prem=prem, theta=theta, curve_type='loglogistic')
    
    row1 = np.array([
        ll_pder2_elr2(c=c, elr=elr),
        ll_pder2_elr_warp(prem=prem, age=age, theta=theta, age_diff=age_diff),
        ll_pder2_elr_theta(prem=prem, age=age, theta=theta, age_diff=age_diff)
    ])
    row2 = np.array([
        ll_pder2_elr_warp(prem=prem, age=age, theta=theta, age_diff=age_diff),
        ll_pder2_warp2(c=c, prem=prem, age=age, theta=theta, age_diff=age_diff, elr=elr),
        ll_pder2_theta_warp(c=c, prem=prem, age=age, theta=theta, age_diff=age_diff, elr=elr)
    ])
    row3 = np.array([
        ll_pder2_elr_theta(prem=prem, age=age, theta=theta, age_diff=age_diff),
        ll_pder2_theta_warp(c=c, prem=prem, age=age, theta=theta, age_diff=age_diff, elr=elr),
        ll_pder2_warp2(c=c, prem=prem, age=age, theta=theta, age_diff=age_diff, elr=elr)  
    ])
    m = np.vstack([row1, row2, row3])
    return(m)

def rao_cramer_lower_bound(origin, c, prem, age, theta, sigma2, age_diff=3, curve_type='loglogistic'):
    if curve_type=='loglogistic':
        i = ll_info_matrix(origin=origin, c=c, prem=prem, age=age, theta=theta, age_diff=age_diff)
        
    i_inv = np.linalg.inv(i)
    out = np.multiply(-sigma2, i_inv)
    return(out)
    



## residual analysis

def resid_tbl(df, theta, sigma2, curve_type='loglogistic'):
    resid_df = df.copy()
    resid_df['c'] = resid_df.inc_paid_loss
    resid_df['mu'] = mu_cc(origin=resid_df.treaty_year, age=resid_df.dev_month, paid=resid_df.inc_paid_loss, 
                     prem=resid_df.deal_est_prem, theta=theta, curve_type=curve_type)
    resid_df['raw_resid'] = resid_df.c - resid_df.mu
    resid_df['normalizing_fct'] = np.sqrt(np.multiply(resid_df.mu.to_numpy(), sigma2))
    resid_df['normalized_resid'] = np.divide(resid_df.raw_resid.to_numpy(), np.sqrt(np.multiply(resid_df.mu.to_numpy(), sigma2)))
    return(resid_df)
    
    
def lift_plot(df, theta, sigma2, ax, curve_type='loglogistic', num_bars=10):

    lift_df = resid_tbl(df=df, theta=theta, sigma2=sigma2, curve_type=curve_type).query('c > 0')
    lift_df['predicted_lr'] = lift_df.mu / lift_df.deal_est_prem
    lift_df['actual_lr'] = lift_df.c / lift_df.deal_est_prem
    lift_df.sort_values('predicted_lr', inplace=True)
    q10 = int(np.floor(lift_df.shape[0]/num_bars))

    buckets = []
    for i in range(num_bars):
        for x in range(q10):
            buckets.append(i+1)

    while len(buckets) < lift_df.shape[0]:
        buckets.append(num_bars)

    lift_df['bucket'] = buckets


    lift_df_gp = lift_df['bucket actual_lr predicted_lr'.split()].groupby('bucket', observed=True).mean()
    # lift_df_gp = lift_df_gp.reset_index().drop('deal_name treaty_year'.split(), 1).groupby('bucket').sum().reset_index()
    # lift_df_gp['actual_lr'] = lift_df_gp.c / lift_df_gp.deal_est_prem
    # lift_df_gp['predicted_lr'] = lift_df_gp.mu / lift_df_gp.deal_est_prem

    # fig, ax = plt.subplots(figsize=figsize)

    # lift_df_gp.reset_index().boxplot('bucket', 'actual_lr')
    # lift_df_gp.reset_index().plot(kind='line', x='bucket', y='predicted_lr', ax=ax, ls='--', )
    lift_df_gp.reset_index().plot(kind='bar', x='bucket', y='actual_lr', title='Incremental Loss Ratio Lift Plot\nActual Loss Ratios Sorted by Modeled Loss Ratio', ax=ax
    # , 
    # ylabel='Average of Actual Loss Ratio in Group', 
    # xlabel='{}-tile Bucket'.format(num_bars)
    )
    plt.show()


def results_tbl(df, theta, cur_year, cur_month, curve_type):
    elr = elr_cc(origin=df.treaty_year, 
                     age=df.dev_month, 
                     paid=df.inc_paid_loss, 
                     prem=df.deal_est_prem, 
                     theta=theta)
    prem_df = df['deal_name treaty_year deal_est_prem'.split()].copy().drop_duplicates().set_index('deal_name treaty_year'.split())
    results_df = df['treaty_year deal_name inc_paid_loss'.split()].groupby('treaty_year deal_name'.split(), observed=True).sum().reset_index()
    results_df = results_df.set_index('deal_name treaty_year'.split()).join(prem_df, how='left')['deal_est_prem inc_paid_loss'.split()].rename(columns=dict(inc_paid_loss='cum_paid_loss')).reset_index()
    results_df['cur_age'] = 12*(cur_year - results_df.treaty_year) + cur_month
    results_df['ave_age'] = results_df.cur_age - 1.5
    results_df['G'] = G(age=results_df.ave_age, theta=theta, curve_type=curve_type)
    results_df['LDF'] = 1 / results_df.G
    results_df['ult_loss'] = (results_df.cum_paid_loss + ((1-results_df.G)*results_df.deal_est_prem*elr)).round(0)
    results_df['unpaid_loss'] = results_df.ult_loss - results_df.cum_paid_loss.round(0)
    results_df['ult_loss_000'] = (results_df.cum_paid_loss * results_df.LDF / 1000).round(0).astype(int)
    results_df['unpaid_000'] = results_df.ult_loss_000 - (results_df.cum_paid_loss / 1000).round(0).astype(int)
    return(results_df)
    
def actual_expected_dist_plot(df, col, treaty_query='treaty_year > 1900', figsize=(15,8)):
    dat = df['treaty_year cy cm dev_month c mu'.split()].query('({}) and (c != 0)'.format(treaty_query))
    dat['actual / expected'] = df.c / df['mu']
    dat['cycm'] = dat['cy cm'.split()].apply(lambda x: str(x[0]) + '-' + ('0' if x[1]<10 else '') + str(x[1]), axis=1)
    fig, ax = plt.subplots(figsize=figsize)
    x = pd.DataFrame({col:dat[col].sort_values().drop_duplicates().astype('category'), 'y':np.ones(dat[col].sort_values().drop_duplicates().shape)})
    sb.violinplot(x=col, y='actual / expected', data=dat, ax=ax, inner='stick', ylabel='Actual Incr. Loss / Modeled Incr. Loss')
    x.rename(columns=dict(y='Expectation of 1.000')).plot(x=col, y='Expectation of 1.000', ax=ax, ls='--', title=f'Actual/Expected Distributions by {col}')
    plt.show()
    
def cum_actual_expected_plot(df, col, figsize=(15,10)):
    dat = df.copy()
    dat['cycm'] = dat['cy cm'.split()].apply(lambda x: str(x[0]) + '-' + ('0' if x[1]<10 else '') + str(x[1]), axis=1)
    fig, ax = plt.subplots(2, 1, figsize=figsize)
    dat.query('c != 0')[[col] + 'c mu'.split()].groupby(col).sum().plot(kind='bar', ax=ax[0], title=f'Cumulative Loss, Actual & Fitted, by {col}')
    l = dat.query('c != 0')[[col] + 'c mu'.split()].groupby(col).sum().reset_index()
    l['actual / modeled'], l['ideal ratio of 1.000'], l[col] = l.c / l.mu, 1, l[col].astype('category')
    l[[col] + ['ideal ratio of 1.000']].set_index(col).plot(ax=ax[1], ls='--', color='black')
    l[[col] + ['actual / modeled']].set_index(col).plot(ax=ax[1], title=f'Cumulative Actual Loss / Cumulative Modeled Loss by {col}')
    plt.show()
    
def actual_expected_scatterplot(df, col, ax, lim=15, alpha=0.7, linewidth=1):
    dat = df.query('((c > 0) and (mu > 0))').assign(c_ln=np.log(df.c), mu_ln=np.log(df.mu))
    col1 = col.replace("_", " ").title()
    dat[col1]=dat[col].astype('category')
    sb.scatterplot(x='c_ln', 
                   y='mu_ln', 
                   data=dat, 
                   hue=col1, 
                   ax=ax, 
                   edgecolor='black',
                   alpha=alpha,
                   linewidth=linewidth
                   )

    ax.plot([0, lim],[0, lim])
    ax.set_xlabel('Actual (Log-Scale)'), ax.set_ylabel('Modeled (Log-Scale)')

    ax.set_title('Actual vs Expected (Log-Scale)\nColors Changing by {}\nn: {}'.format(col.replace('_', ' ').title(), df.query('((c > 0) and (mu > 0))').shape[0]))

    plt.show()
    
def process_variance_df(df, sigma2):  
    var_df = df.copy()
    # var_df['unpaid_loss'] = var_df.ult_loss - var_df.cum_paid_loss
    # var_df.drop('ult_loss', 1, inplace=True)

    # var_df = var_df.reset_index(drop=True).groupby('treaty_year').sum().reset_index()

    var_df['process_var'] = sigma2 * var_df.unpaid_loss
    var_df['process_sd'] = np.sqrt(var_df.process_var)
    var_df['process_cv'] = var_df.process_sd / var_df.unpaid_loss
    var_df = var_df.sort_values('treaty_year').assign(lr=((var_df.cum_paid_loss + var_df.unpaid_loss)/var_df.deal_est_prem))
    
    return(var_df)
    
def reserve_cc(origin, c, prem, theta, age, cur_year, cur_month, return_reserve=False, divide_by=1000, curve_type='loglogistic'):
    g1 = lambda x: G(age=age, theta=x[:2], curve_type=curve_type)
    prior_age=age.apply(lambda x: 0 if x <=3 else x-3)
    g0 = lambda x: G(age=prior_age, theta=x[:2], curve_type=curve_type)

    df = pd.DataFrame(dict(origin=origin, prem=prem, c=c, age=age))
    df['age_0'] = df.age.apply(lambda x: 0 if x<=3 else x-3)
    df["g1"] = g1(theta)
    df["g0"] = g0(theta)
    df['diff'] = df.g1 - df.g0
    df['resv_term'] = df.prem * theta[2] * df['diff']
    df['mu'] = df.resv_term
    
    premdf = df['origin prem'.split()].drop_duplicates().groupby('origin').sum().reset_index()
    result_df = (df.copy().drop('prem age age_0 g1 g0 diff'.split(), 1).groupby('origin').sum()).reset_index().rename(columns=dict(c='paid_loss_dcce')).drop('resv_term', 1)
    result_df = (result_df.merge(premdf, how='left', on='origin').set_index('origin')).reset_index()
    
    result_df['cur_age'] = result_df.origin.astype(int).apply(lambda x: 12 * (cur_year - x) + cur_month)
    result_df['ave_age'] = result_df['cur_age'].apply(lambda x: x-6)
    result_df['pct_paid'] = result_df.ave_age.apply(lambda x: np.divide(np.power(x, theta[0]), np.power(x, theta[0]) + np.power(theta[1], theta[0])))
    result_df['unpaid'] = result_df.prem * (1 - result_df.pct_paid) * theta[2]
    result_df['ult'] = result_df.paid_loss_dcce + result_df.unpaid
    result_df['lr'] = result_df.ult / result_df.prem
    
    out = (result_df.set_index('origin cur_age ave_age pct_paid lr'.split())/divide_by).round(0).reset_index()
#     result_df['lr%'] = (100 * (result_df.paid_loss_dcce + result_df.modeled_unpaid) / result_df.prem).round(2)
    
    
#     result_df['origin'] = result_df['origin'].astype(str)
    
#     g = lambda x: ccf.G(age=df.age, theta=x, curve_type=clark['fitdat']['curve_type_0'])
#     g_grad = pd.DataFrame(nd.Gradient(g)(theta), columns='warp theta elr'.split()).sum()

    if return_reserve:
        total_df = pd.DataFrame(dict(origin=['Total'], reserve=[result_df.unpaid.sum()]))
        out = out['origin unpaid'.split()].rename(columns=dict(unpaid='reserve'))
        out = pd.concat([out['origin reserve'.split()], total_df]).set_index('origin').reserve
    
    return(out)
    
def reserve_cc2(origin, loss, prem, age, theta, curve_type='loglogistic'):
    df = pd.DataFrame(dict(origin=origin, prem=prem, loss=loss, age=age))
    df['G'] = df.age.apply(lambda x: G(x, theta[:(len(theta)-1)], curve_type=curve_type))
    df1 = df.copy().query('origin != "Total"')
    df1['elr'] = theta[len(theta)-1]
    df1['unpaid'] = df1.prem * df1.elr * (1 - df1.G)
    dft = pd.DataFrame(df1.drop('origin', 1).sum()).transpose().assign(origin='Total')
    out = pd.concat([df1, dft])
    return(out.set_index('origin').unpaid)
    
def reserve_process_variance(reserve, sigma2):
    out = (sigma2 * reserve).to_numpy()
    return(out)
    
def reserve_parameter_variance(reserve_gradient, var_covar_matrix):
    s = reserve_gradient.shape[0]
    out = []
    
    for i in range(s):
        fct1 = reserve_gradient[i, :]
        fct2 = var_covar_matrix
        fct3 = np.transpose(fct1)
    
        m1 = np.matmul(fct1, fct2)
        m2 = np.matmul(m1, fct3)
        out.append(m2)
    
    return(np.array(out))
  
def reserve_gradient(origin, loss, prem, age, theta, curve_type='loglogistic'): 
    
    # g1 = lambda x: G(age=age, theta=x[:2], curve_type=curve_type)
    # prior_age=age.apply(lambda x: 0 if x <=3 else x-3)
    # g0 = lambda x: G(age=prior_age, theta=x[:2], curve_type=curve_type)
    rgradftn = lambda x: reserve_cc2(origin=origin, loss=loss, prem=prem, age=age, theta=x, curve_type=curve_type)
    reserve_grad = pd.DataFrame(nd.Gradient(rgradftn)(theta), index=rgradftn(theta).index.tolist(), columns='warp theta elr'.split())
    reserve_grad['reserve'] = rgradftn(theta)
    return(reserve_grad)