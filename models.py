import numpy as np
from utils import *

def batchCusum(x, mean, std, min_shift = .5, max_influence = 4):
    """CUSUM algorithm for change point detection
    x  : 1D np.array
    mean: estimated center of the distribution of x[0]
    std: estimated standard deviation of the distribution of x[0]
    min_shift: minimum shift size to consider
    max_influence: the maximum influence of a single data point
    """
    
    # Normalize x
    x = (x - mean) / std
    
    # Compute positive and negative CUSUM stats
    Cp = np.zeros_like(x)
    Cn = np.zeros_like(x)
    for i in range(len(x)):
        if i > 0:
            psignal = np.min([max_influence, x[i] - min_shift])
            nsignal = np.min([max_influence, -x[i] - min_shift])
            Cp[i] = np.max([0, psignal + Cp[i-1]])
            Cn[i] = np.max([0, nsignal + Cn[i-1]])
            
    # Final statistic is max of Cp and Cn
    return np.maximum(Cp, Cn)

def cusum(x, startup = 10, threshold=6, verbose=False):
    """Apply CUSUM algorithm after each new data point
    x: 1D np.array with at least (startup) points
    startup: number of points to bootstrap initial std guess
    threshold: threshold for cusum stat before declaring a change point
    verbose: controls debug messages
    """
    n = len(x)
    
    # Things to keep track of
    cusumStats = [np.full(n, np.nan)]
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
        batchOutput = batchCusum(x[i:j], np.median(x[i:j]), stdEsts[j])
        cusumStats[-1][j] = batchOutput[-1]
        if verbose: 
            print('idx: %d | CUSUM: %f | std: %f' % (j, cusumStats[-1][j], stdEsts[j]))
        if cusumStats[-1][j] >= threshold:
            # Backtrack to find where previous regime ended (where CUSUM stat was last small)
            regLen = np.amax(np.where(batchOutput < threshold/4)) + 1
            i += regLen
            changePts.append(i)
            
            cusumStats.append(np.full(n, np.nan))
            
            if verbose:
                print('At idx %d, changepoint detected at idx %d' % (j, i))
            
            # Now that we know i is a change point, go back to i and recalculate CUSUM
            preStd = stdEsts[i-1]
            j = i+1
        
        else:
            j += 1
    return {'x': x, 'cusum': cusumStats, 'std': stdEsts}, changePts