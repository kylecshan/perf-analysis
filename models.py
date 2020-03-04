import numpy as np
import pandas as pd
from scipy.stats import t as tdist
from basicstats import *
from utils import *

def glrmean(x, alpha, num_test=5):
    '''
    For each potential split point in a time series, perform a generalized
    likelihood test for a difference in the mean (equivalent to t-test for normal)
    Input:
        x        : time series input
        alpha    : significance level (e.g. 0.001). Since we perform multiple
                   hypothesis tests, we use the Bonferroni correction to avoid
                   inflated p-values (e.g. if testing 8 potential changepoints,
                   each changepoint is tested at the 0.001/8 significance level)
        num_test : rank the first-order differences and only consider this many of
                   the largest differences (by absolute value). Making this smaller
                   saves time and increases the power of the test (assuming true
                   changepoint corresponds to a large change).
    Output:
        chgPts: None if no significant changepoint detected, otherwise the index of
                the detected changepoints (where i is a changepoint iff there was a
                change between i-1 and i)
        stats : t-stats associated with chgPts
    '''
    x = make_numpy(x)
    chgPts = []
    stats = []
    n = len(x)
    if n <= 2:
        return [], []
    
    # Performing (n-minRegime) t-tests; apply Bonferroni correction
    threshold = tdist.isf(alpha/(2*num_test), df=n-2)
    # To save time, only check a few largest jumps in absolute value
    largest_jumps = 1 + np.argsort(
        [np.abs(x[i]-x[i-1]) for i in range(1, n)]
    )[-num_test:]
    for k in largest_jumps:
        T = ttest(x[:k], x[k:])
        if np.abs(T) >= threshold: 
            chgPts.append(k)
            stats.append(T)
    return chgPts, stats
        
class VoteHistory:
    '''
    Helper class for changepoint finder. Stores the candidate changepoints
    detected by several sources, and determines whether they agree on any.
    '''
    def __init__(self, num_votes):
        self.votes = [set() for _ in range(num_votes)]
    def push(self, vote_list):
        self.votes.append(set(vote_list))
        self.votes.pop(0)
    def result(self):
        unanimous = set.intersection(*self.votes)
        return None if unanimous == set() else min(unanimous)
    def reset(self):
        self.votes = [set() for _ in self.votes]
    
def find_chgpts(x, alpha=0.0001, min_agree=3, verbose=False):
    '''
    Apply changepoint detection method sequentially
    Inputs:
        x        : time series input
        threshold: threshold value to pass into the underlying model
        min_agree: minimum consecutive agreeing detections to determine a changepoint
        verbse   : print some output while using
    Outputs:
        changePts: list of detected changepoints (indices of x)
        detectPts: list of indices at which corresponding changepoints were detected
                   (a changepoint may not be detected until several observations after
                   the change)
    '''
    x = make_numpy(x)
    n = len(x)
    if n <= 2:
        return [0], [0]
    
    chgpts = [0]    # Identified changepoints
    detpts = [0]    # When each corresponding changepoint is detected
    votes = VoteHistory(min_agree) # Require a few consecutive detections of the same changepoint
    i = 0           # Track the last detected changepoint
    j = i+1         # Consider data up to (but not including) index j
    while j <= n:
        # Find changepoints in x[i:j]
        vote_list, stats = glrmean(x[i:j], alpha)
        votes.push(vote_list)
        chgpt = votes.result()
        if chgpt is not None:
            i += chgpt
            chgpts.append(i)
            detpts.append(j-1)
            if verbose:
                print('At idx %d, changepoint detected at idx %d' % (j-1, i))
            
            # Now that we know i is a change point, go back to i
            j = i+1
            votes.reset()
        else:
            j += 1
    return chgpts, detpts, votes