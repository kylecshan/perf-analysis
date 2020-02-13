import numpy as np
import pandas as pd
from scipy.stats import t
from utils import *
    
# def weightedStd(priorStd, priorN, x):
#     """Weighted average of a prior estimate of std and std of current sample
#     """
#     n = len(x)
#     if n < 4:
#         return priorStd
    
#     std = trimStd(x)
#     postStd = (priorN * priorStd + n * std) / (priorN + n)
#     return postStd

def trimmedStats(x, end=0):
    return trimMean(x, end=0), trimStd(x, end=0)**2

def ttest(xl, xr):
    lmean, lvar = trimmedStats(xl)
    rmean, rvar = trimmedStats(xr)

    k = len(xl)
    n = len(xl)+len(xr)
    
    rss = (k-1)*lvar + (n-k-1)*rvar
    sigma = np.sqrt(rss/(n-2))
    
    T = np.sqrt(k*(n-k)/n)*(lmean-rmean)/sigma
    return T
    
def glrmean(x, threshold, minRegime=3):
    """Scan through range to find partition which maximizes t-test for change
    in the mean
    """
    best = 0
    chgPt = None
    n = len(x)
    if n <= minRegime:
        return chgPt, 0
    
    # Performing (n-minRegime) t-tests; apply Bonferroni correction
    threshold = t.isf(threshold/(2*(n-minRegime)), df=n-2)
    for k in range(minRegime, n):
        T = ttest(x[:k], x[k:])
        if np.abs(T) > best:
            best = np.abs(T)
            if np.abs(T) >= threshold: 
                chgPt = k
    return chgPt, best

def glrvar(x, threshold, minSample = 6):
    """Scan through range to find partition which maximizes test for change
    in the var
    """
    best = 0
    chgPt = None
    n = len(x)
    if n < minSample:
        return chgPt, 0
    for k in range(minSample, n-minSample+1):
        lmean, lvar = trimmedStats(xl)
        rmean, rvar = trimmedStats(xr)
        
        rss = (k-1)*lvar + (n-k-1)*rvar
        var = rss/(n-2)
        
        C = 1+( 1/(k-1) + 1/(n-k-1) - 1/(n-2) )/3
        G = ( (k-1)*np.log(var/lvar) + (n-k-1)*np.log(var/rvar) ) / C
        if G > best:
            best = G
            if G >= threshold:
                chgPt = k
    return chgPt, best
        
    
def findChangePts(x, threshold=6, minRegime = 3, method='mean', verbose=False):
    """Apply CUSUM algorithm after each new data point
    x: 1D np.array
    threshold: threshold for declaring a change point (interpretation depends on model)
    minRegime: minimum number of data points between changepoints
    method: whether to look for a change in mean ('mean') or variance ('var')
    verbose: controls debug messages
    """
    n = len(x)
    if n < 4:
        return [0]
    assert(method in ['mean', 'var'])
    
    # Investigate the current regime for evidence of a new regime.
    changePts = [0] # Identified changepoints
    detectPts = [0] # When each corresponding changepoint is detected
    i = changePts[-1]
    j = i+1
    while j < n:
        # Calculate stat and check if it's over the threshold
        if method == 'mean':
            chgPt, _ = glrmean(x[i:j], threshold, minRegime)
        elif method == 'var':
            chgPt, _ = glrvar(x[i:j], threshold)
        
        if chgPt is not None:
            i += chgPt
            changePts.append(i)
            detectPts.append(j)
            
            if verbose:
                print('At idx %d, changepoint detected at idx %d' % (j, i))
            
            # Now that we know i is a change point, go back to i and recalculate CUSUM
            j = i+1
        
        else:
            j += 1
    return changePts, detectPts