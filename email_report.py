# Import libraries
import numpy as np
from models import find_chgpts, glrmean

def changepoint_test(wtimes, alpha=0.005):
    '''
    Use changepoint detection model to determine if latest observation(s) indicate a change
    in performance. Input should be sorted chronologically.
    
    Returns:
        status, measured, mean, std
    Status:
        'fail' if there is a changepoint associated with a significant performance drop,
               which has been detected for a few consecutive days
        'warn' if there is a changepoint associated with a significant performance drop,
               but we are waiting for more observations to confirm
        'pass' otherwise (no performance drops detected)
    '''
    min_agree = 3 # Number of consecutive times a changepoint must be detected
    num_test = 10  # Consider only the largest changes in timers as potential changepoints
    lookback = 30 # Limit lookback window
    
    wt = np.asarray(wtimes, dtype=np.float64)
    wt = np.log(wt)
    
    # Find latest changepoint based on previously known information
    chgpts, detpts, votes = find_chgpts(wt[:-1], alpha, min_agree, num_test, lookback)
    
    # Only consider data since the latest previously-known changepoint, subj to max lookback window
    last_known = max(chgpts[-1], len(wt) - lookback)
    wt_recent = wt[last_known:]
    
    vote_list, tstats = glrmean(wt_recent, alpha, num_test)
    perf_drops = {vote+last_known: tstat for vote, tstat in zip(vote_list, tstats) if tstat > 0}
    
    votes.push(perf_drops)
    if votes.result() is not None:
        status = 'fail'
    elif len(perf_drops) > 0:
        status = 'warn'
    else:
        status = 'pass'
       
    # Also compute the mean and standard deviation since the last previously-detected changepoint
    mu = np.exp(wt_recent).mean()
    sig = np.exp(wt_recent).std()
        
    return status, np.exp(wt[-1]), mu, sig
