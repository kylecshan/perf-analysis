import numpy as np
import pandas as pd
from scipy.stats import t as tdist
from basicstats import *
from utils import *

def glrmean(x, alpha, num_test=None):
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
    n = len(x)
    if n <= 2:
        return [], []
    if num_test is None:
        num_test = n-1
    
    chgPts = []
    stats = []
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
        self.votes = [dict() for _ in range(num_votes)]
    def push(self, vote_dict):
        self.votes.append(vote_dict)
        self.votes.pop(0)
    def result(self):
        unanimous = set.intersection(*[set(d.keys()) for d in self.votes])
        if len(unanimous) == 0:
            return None
        else:
            options = [(k, sum(d[k] for d in self.votes)) for k in unanimous]
            best_option = max(options, key=lambda x: np.abs(x[1]))
            return best_option[0]
    def reset(self):
        self.votes = [dict() for _ in self.votes]
    
def find_chgpts(x, alpha=0.0001, min_agree=3, num_test=5, lookback=30, verbose=False):
    '''
    Apply changepoint detection method sequentially
    Inputs:
        x        : time series input
        threshold: threshold value to pass into the underlying model
        min_agree: minimum consecutive agreeing detections to determine a changepoint
        num_test : only test this many of the largest changes - can save some time by
                   not considering every single data point as a potential changepoint
        lookback : max number of data points to look backward in time (avoid hyper-
                   sensitivity as sample size grows)
        verbse   : print some output while using
    Outputs:
        changePts: list of detected changepoints (indices of x)
        detectPts: list of indices at which corresponding changepoints were detected
                   (a changepoint may not be detected until several observations after
                   the change)
    '''
    chgpts = [0]    # Identified changepoints
    detpts = [0]    # When each corresponding changepoint is detected
    votes = VoteHistory(min_agree)
    
    x = make_numpy(x)
    n = len(x)
    if n <= 2:
        return chgpts, detpts, votes
        
    i = 0           # Track starting point of current data under consideration
    j = i+1         # Consider data up to (but not including) index j
    while j <= n:
        # Find changepoints in x[i:j]
        vote_list, stats = glrmean(x[i:j], alpha, num_test)
        votes.push({vote+i: stat for vote, stat in zip(vote_list, stats)})
        chgpt = votes.result()
        if chgpt is not None:
            i = chgpt
            chgpts.append(chgpt)
            detpts.append(j-1)
            if verbose:
                print('At idx %d, changepoint detected at idx %d' % (j-1, i))
            
            # Now that we know i is a change point, go back to there
            j = chgpts[-1]+1
            votes.reset()
        else:
            j += 1
            i = max(i, j-lookback)
    return chgpts, detpts, votes

# Used for parallelizing
def single_ts_chgpts(my_input):
    key, data, threshold = my_input
    pts = find_chgpts(data['time'], alpha=threshold)[0]
    return key, pts