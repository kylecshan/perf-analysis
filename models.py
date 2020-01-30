import numpy as np
import pandas as pd
from scipy.stats import t
from utils import *
    
def weightedStd(priorStd, priorN, x):
    """Weighted average of a prior estimate of std and std of current sample
    """
    n = len(x)
    if n < 4:
        return priorStd
    
    std = trimStd(x)
    postStd = (priorN * priorStd + n * std) / (priorN + n)
    return postStd

def glrmean(x, mean, std, threshold):
    """CUSUM algorithm for change point detection
    x  : 1D np.array
    mean: estimated center of the distribution of x[0]
    std: estimated standard deviation of the distribution of x[0]
    threshold: minimum likelihood ratio for detection
    
    returns: index of first detected change point, highest significance
    """
    
    # Normalize x
    x = (x - mean) / std
    
    # Find minimum n that yields a detection
    lrs = np.array([np.nan])
    chgPt = None
    for n in range(2, len(x)+1):
        S = np.cumsum(x[:n])
        lrs = np.array([np.abs(S[n-1]-S[k])/np.sqrt(n-k-1) for k in range(n-1)])
        if np.any(lrs >= threshold):
            chgPt = n-1
            break
    return chgPt, np.amax(lrs)

def ttest(x, threshold):
    """Scan through range to find partition which maximizes t-test for change
    in the mean
    """
    best = 0
    chgPt = None
    n = len(x)
    if n < 4:
        return chgPt, 0
    
#     threshold = t.isf(threshold/(2*(n-2)), df=n-2)
    for k in range(1, n):
        rmean = trimMean(x[k:], end=0)
        lmean = trimMean(x[:k], end=0)
        rvar = trimStd(x[k:], end=0)**2
        lvar = trimStd(x[:k], end=0)**2
        
        rss = (k-1)*lvar + (n-k-1)*rvar
        sigma = np.sqrt(rss/(n-2))
        T = np.sqrt(k*(n-k)/n)*(lmean-rmean)/sigma
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
        rmean = trimMean(x[k:], end=0)
        lmean = trimMean(x[:k], end=0)
        rvar = trimStd(x[k:], end=0)**2
        lvar = trimStd(x[:k], end=0)**2
        
        rss = (k-1)*lvar + (n-k-1)*rvar
        var = rss/(n-2)
        
        C = 1+( 1/(k-1) + 1/(n-k-1) - 1/(n-2) )/3
        G = ( (k-1)*np.log(var/lvar) + (n-k-1)*np.log(var/rvar) ) / C
        if G > best:
            best = G
            if G >= threshold:
                chgPt = k
    return chgPt, best
        
    
def findChangePts(x, startup = 10, threshold=6, method='glrmean', verbose=False):
    """Apply CUSUM algorithm after each new data point
    x: 1D np.array with at least (startup) points
    startup: number of points to bootstrap initial std guess
    threshold: threshold for cusum stat before declaring a change point
    method: which method to use {'glrmean', 'ttest', 'glrvar'}
    verbose: controls debug messages
    """
    n = len(x)
    
    # Things to keep track of
    changePts = [0]
    stdEsts = np.zeros(n)
    
    # Steal some initial data for an initial guess about std
    stdEsts[:startup] = np.std(x[:startup])
    preStd = stdEsts[startup-1]
    preWt = 5 # Use previous regime's stdev as if it was this much data
    
    # Investigate the current regime for evidence of a new regime.
    i = changePts[-1]
    j = i+1
    while j < n:
        # Estimate variance of current regime
        stdEsts[j] = weightedStd(preStd, preWt, x[i:j])
        
        # Calculate CUSUM stat and check if it's over the threshold
        if method == 'glrmean':
            chgPt, _ = glrmean(x[i:j], x[i], stdEsts[j], threshold)
        elif method == 'ttest':
            chgPt, _ = ttest(x[i:j], threshold)
        elif method == 'glrvar':
            chgPt, _ = glrvar(x[i:j], threshold)
        else:
            print('Method not recognized')
            return
        
        if chgPt is not None and chgPt > 1: #len(batchOut) > 1 and np.any(batchOut >= threshold):
#             print(len(batchOut), chgPt, np.amax(batchOut))
#             regimeLen = chgPt
            i += chgPt
            changePts.append(i)
            
            if verbose:
                print('At idx %d, changepoint detected at idx %d' % (j, i))
            
            # Now that we know i is a change point, go back to i and recalculate CUSUM
            preStd = stdEsts[i-1]
            j = i+1
        
        else:
            j += 1
    return changePts, stdEsts

  

# def batchCusum(x, mean, std, min_shift = .5, max_influence = 4):
#     """CUSUM algorithm for change point detection
#     x  : 1D np.array
#     mean: estimated center of the distribution of x[0]
#     std: estimated standard deviation of the distribution of x[0]
#     min_shift: minimum shift size to consider
#     max_influence: the maximum influence of a single data point
#     """
    
#     # Normalize x
#     x = (x - mean) / std
    
#     # Compute positive and negative CUSUM stats
#     Cp = np.zeros_like(x)
#     Cn = np.zeros_like(x)
#     for i in range(len(x)):
#         if i > 0:
#             psignal = np.min([max_influence, x[i] - min_shift])
#             nsignal = np.min([max_influence, -x[i] - min_shift])
#             Cp[i] = np.max([0, psignal + Cp[i-1]])
#             Cn[i] = np.max([0, nsignal + Cn[i-1]])
            
#     # Final statistic is max of Cp and Cn
#     return np.maximum(Cp, Cn)

# def cusum(x, startup = 10, threshold=6, max_influence=4, verbose=False):
#     """Apply CUSUM algorithm after each new data point
#     x: 1D np.array with at least (startup) points
#     startup: number of points to bootstrap initial std guess
#     threshold: threshold for cusum stat before declaring a change point
#     verbose: controls debug messages
#     """
#     n = len(x)
    
#     # Things to keep track of
#     cusumStats = [np.full(n, np.nan)]
#     changePts = [0]
#     stdEsts = np.zeros(n)
    
#     # Steal some initial data for an initial guess about std
#     stdEsts[:startup] = np.std(x[:startup])
#     preStd = stdEsts[startup-1]
#     preWt = 5 # Use previous regime's stdev as if it was this much data
    
#     # Investigate the current regime for evidence of a new regime.
#     i = changePts[-1]
#     j = i+1
#     while j < n:
#         # Estimate variance of current regime
#         stdEsts[j] = weightedStd(2*preStd, preWt, x[i:j])
        
#         # Calculate CUSUM stat and check if it's over the threshold
#         batchOutput = batchCusum(x[i:j], np.median(x[i:j]), stdEsts[j], max_influence=max_influence)
#         cusumStats[-1][j] = batchOutput[-1]
#         if verbose: 
#             print('idx: %d | CUSUM: %f | std: %f' % (j, cusumStats[-1][j], stdEsts[j]))
#         if cusumStats[-1][j] >= threshold:
#             # Backtrack to find where previous regime ended (where CUSUM stat was last small)
#             regLen = np.amax(np.where(batchOutput < threshold/4)) + 1
#             i += regLen
#             changePts.append(i)
            
#             cusumStats.append(np.full(n, np.nan))
            
#             if verbose:
#                 print('At idx %d, changepoint detected at idx %d' % (j, i))
            
#             # Now that we know i is a change point, go back to i and recalculate CUSUM
#             preStd = stdEsts[i-1]
#             j = i+1
        
#         else:
#             j += 1
#     return {'x': x, 'cusum': cusumStats, 'std': stdEsts}, changePts