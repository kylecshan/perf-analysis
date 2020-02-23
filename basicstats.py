import datetime as dt
import numpy as np
import pandas as pd
from scipy.stats import t
from utils import trim


def trimMean(x, p=.125, end=0):
    '''
    Trim a series to remove egregious outliers, and then return the mean.
    Input:
        x  : series to trim
        p  : maximum proportion of data to remove
        end: number of data points to remove from the end of the series
    '''
    return trim(x, p, end).mean()

def trimStd(x, p=.125, end=0):
    '''
    Trim a series to remove egregious outliers, and then return the standard deviation.
    Inputs:
        x  : series to trim
        p  : maximum proportion of data to remove
        end: number of data points to remove from the end of the series
    '''
    return trim(x, p, end).std()

def trimmedStats(x, end=0):
    '''
    Get trimmed mean and variance
    '''
    return trimMean(x, end=0), trimStd(x, end=0)**2

def ttest(xl, xr):
    '''
    Get t-statistic for difference in two independent samples with unequal variance
    Input:
        xl, xr: samples to compare
    '''
    lmean, lvar = trimmedStats(xl)
    rmean, rvar = trimmedStats(xr)

    k = len(xl)
    n = len(xl)+len(xr)
    
    rss = (k-1)*lvar + (n-k-1)*rvar
    sigma = np.sqrt(rss/(n-2))
    
    T = np.sqrt(k*(n-k)/n)*(lmean-rmean)/sigma
    return T
    
def regimeTimeseries(y, changePts):
    '''
    Given a timeseries y and a set of changepoints, return two timeseries with the
    same length as y containing the mean and standard deviation computed within each
    pair of consecutive changepoints.
    Inputs:
        y        : time series input
        changePts: sorted list of indices of y which are changepoints, 
                     where changePts[0] = 0
    '''
    n = len(y)
    m = len(changePts)
    mean = np.zeros_like(y)
    std = np.zeros_like(y)
    for i in range(m):
        a = changePts[i]
        b = changePts[i+1] if i < m-1 else n
        mean[a:b] = trimMean(y[a:b])
        std[a:b] = trimStd(y[a:b])
    return mean, std