import datetime as dt
import numpy as np
import pandas as pd
from scipy.stats import t as tdist, median_absolute_deviation as mad
from utils import make_numpy

def trim(x, p=.125, end=0, threshold=3):
    '''
    Remove observations that may be outliers - suspiciously far from the average.
    At most [floor(len(x)*p) + end] points are removed.
    Inputs:
        x  : data to trim
        p  : proportion of data to remove
        end: number of data points at the end of x to ignore
    '''
    # Trim most recent observations
    if len(x) - end < np.ceil(1/p):
        return x
    n = len(x)-end
    x = x[:n]
    # Trim most extreme observations if more than [threshold] std away.
    n_remove = int(np.floor(n*p))
    dev = np.abs(x - np.median(x))/mad(x)
    order = np.argsort(np.abs(x - np.median(x)))
    keep = [i for i in range(n) if dev[i] < threshold or i in order[:n-n_remove]] 
    return x[keep]

def trim_mean(x, p=.125, end=0):
    '''
    Trim a series to remove egregious outliers, and then return the mean.
    Input:
        x  : series to trim
        p  : maximum proportion of data to remove
        end: number of data points to remove from the end of the series
    '''
    return trim(x, p, end).mean()

def trim_std(x, p=.125, end=0):
    '''
    Trim a series to remove egregious outliers, and then return the standard deviation.
    Inputs:
        x  : series to trim
        p  : maximum proportion of data to remove
        end: number of data points to remove from the end of the series
    '''
    return trim(x, p, end).std()

def trimmed_stats(x, end=0, var=True):
    '''
    Get trimmed mean and std or variance
    '''
    if var:
        return trim_mean(x, end=0), trim_std(x, end=0)**2
    else:
        return trim_mean(x, end=0), trim_std(x, end=0)

def ttest(x1, x2=None, with_pval=False):
    '''
    Get t-statistic for difference in two independent samples with unequal variance.
    Useful if the means of the samples are roughly normal (e.g. data is normal, or
    sample size large enough, say 30+)
    Input:
        x1, x2: samples to compare. If x2 is None, performs one-sample t-test of mean==0
    '''
    x1, x2 = make_numpy(x1, x2)
    lmean, lvar = trimmed_stats(x1, var=True)
    if x2 is None:
        n = len(x1)
        tstat = lmean / np.sqrt(lvar/(n-2))
    else:
        rmean, rvar = trimmed_stats(x2, var=True)
        k, n = len(x1), len(x1)+len(x2)
        if n <= 2:
            return (0, 1) if with_pval else 0

        rss = (k-1)*lvar + (n-k-1)*rvar
        sigma = np.sqrt(rss/(n-2))
        tstat = np.sqrt(k*(n-k)/n)*(lmean-rmean)/sigma
    pval = 2*tdist.cdf(-np.abs(tstat), n-2)
    return (tstat, pval) if with_pval else tstat

def permtest(x1, x2, N = 1000, stat = np.mean):
    '''
    Apply permutation test of a given statistic on two samples. Robust to non-normality
    but takes longer to run than a t-test.
    Inputs:
        x1, x2: samples to compare
        N     : number of random permutations to generate
        stat  : function which computes test statistic (e.g. mean, median)
    '''
    x1, x2 = make_numpy(x1, x2)
    x1, x2 = trim(x1), trim(x2)
    actual = stat(x1) - stat(x2)
    combined = np.concatenate((x1, x2))
    nl, nr = len(xl), len(x2)
    def perm_stat(x):
        x = np.random.permutation(x)
        return stat(x[:nl]) - stat(x[nl:])
    samples = [perm_stat(combined) for _ in range(N)]
    pval = (1 + np.sum(np.abs(samples) >= np.abs(actual))) / (N+1)
    return pval
    
def regime_ts(y, changePts, std_error=False):
    '''
    Given a timeseries y and a set of changepoints, return three timeseries with the
    same length as y, containing the mean and upper/lower bounds
    Inputs:
        y        : time series input
        changePts: sorted list of indices of y which are changepoints, 
                     where changePts[0] = 0
        std_error: whether reported std should be std error of the mean
    '''
    y = make_numpy(y)
    n = len(y)
    m = len(changePts)
    mean = np.zeros_like(y)
    upper = np.zeros_like(y)
    lower = np.zeros_like(y)
    for i in range(m):
        a = changePts[i]
        b = changePts[i+1] if i < m-1 else n
        avg, std = trimmed_stats(y[a:b], var=False)
        mean[a:b] = avg
        if std_error:
            std /= np.sqrt(b-a)
            t_crit = tdist.isf(0.01/2, b-a-1)
        else:
            t_crit = 2
        upper[a:b] = mean[a:b] + t_crit*std
        lower[a:b] = mean[a:b] - t_crit*std
    return mean, upper, lower

    
    
    
    
    