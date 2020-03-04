# Import libraries
import numpy as np
from models import find_chgpts, glrmean

def changepoint_test(wtimes, alpha=0.0001):
    '''
    Use changepoint detection model to determine if latest observation(s) indicate a change
    in performance. Input should be sorted chronologically.
    
    Returns:
        status, measured, mean, std
    Status:
        'fail' if there is a changepoint associated with a significant performance drop,
               which has been detected for a few consecutive days
        'warn' if there is a changepoint associated with a significant performance drop,
               but we are waiting for additional confirmation (could be an outlier)
        'pass' otherwise (no performance drops detected)
    '''
    wt = np.asarray(wtimes, dtype=np.float64)
    # Find latest changepoint based on previously known information
    chgpts, detpts, votes = find_chgpts(wt[:-1], alpha=alpha)
    
    # Only consider data since the latest previously-detected changepoint
    last_known = chgpts[-1]
    wt_recent = wt[last_known:]
    
    vote_list, tstats = glrmean(wt_recent, alpha=alpha)
    perf_drops = [vote_list[i] for i, tstat in enumerate(tstats) if tstat > 0]
    
    votes.push(perf_drops)
    if votes.result() is not None:
        status = 'fail'
    elif len(perf_drops) > 0:
        status = 'warn'
    else:
        status = 'pass'
       
    # Also compute the mean and standard deviation since the last previously-detected changepoint
    mu = wt_recent.mean()
    sig = wt_recent.std()
        
    return status, wt[-1], mu, sig
