import numpy as np
import pandas as pd
from scipy.stats import t as tdist
from basicstats import *
from utils import *

def glrmean(x, signif, minRegime, num_test=4):
    '''
    For each potential split point in a time series, perform a generalized
    likelihood test for a difference in the mean (equivalent to t-test for normal)
    Input:
        x        : time series input
        signif   : significance level (e.g. 0.001). Since we perform multiple
                   hypothesis tests, we use the Bonferroni correction to avoid
                   inflated p-values (e.g. if testing 8 potential changepoints,
                   each changepoint is tested at the 0.001/8 significance level)
        minRegime: minimum distance from the beginning to consider as a changepoint
                   (e.g. if minRegime = 3, don't consider x[0], x[1], or x[2] as
                   potential changepoints)
        num_test : rank the first-order differences and only consider this many of
                   the largest differences (by absolute value)
    Output:
        chgPts: None if no significant changepoint detected, otherwise the index of
                the detected changepoints (where i is a changepoint iff there was a
                change between i-1 and i)
        stats : t-stats associated with chgPts
    '''
    chgPts = []
    stats = []
    n = len(x)
    if n <= minRegime+1:
        return [], []
    
    # Performing (n-minRegime) t-tests; apply Bonferroni correction
    threshold = tdist.isf(signif/(2*num_test), df=n-2)
    # To save time, only check a few largest jumps in absolute value
    largest_jumps = minRegime + np.argsort(
        [np.abs(x[i]-x[i-1]) for i in range(minRegime, n)]
    )[-num_test:]
    for k in largest_jumps:
        T = ttest(x[:k], x[k:])
        if np.abs(T) >= threshold: 
            chgPts.append(k)
            stats.append(T)
    return chgPts, stats

# def glrvar(x, threshold, minSample = 6):
#     """
#         For each potential split point in a time series, perform a generalized
#     likelihood test for a difference in the variance.
#     Input:
#         x        : time series input
#         threshold: numeric threshold for detection (e.g. 10). No easy way to translate
#                    between this value and a significance level.
#         minRegime: minimum amount of data on either end of the regime
#     Output:
#         chgPt: None if no significant changepoint detected, otherwise the index of
#                  the detected changepoint
#         best : Highest statistic detected (this is over the threshold iff chgPt is
#                not None). If not enough data, then 0.
#     """
#     best = 0
#     chgPt = None
#     n = len(x)
#     if n < minSample:
#         return chgPt, 0
#     for k in range(minSample, n-minSample+1):
#         lmean, lvar = trimmedStats(xl)
#         rmean, rvar = trimmedStats(xr)
        
#         rss = (k-1)*lvar + (n-k-1)*rvar
#         var = rss/(n-2)
        
#         C = 1+( 1/(k-1) + 1/(n-k-1) - 1/(n-2) )/3
#         G = ( (k-1)*np.log(var/lvar) + (n-k-1)*np.log(var/rvar) ) / C
#         if G > best:
#             best = G
#             if G >= threshold:
#                 chgPt = k
#     return chgPt, best
        
# Helper class for changepoint finder.
class VoteHistory:
    def __init__(self, numVotes):
        self.votes = [set() for _ in range(numVotes)]
    def insert(self, voteList):
        self.votes.append(set(voteList))
        self.votes.pop(0)
    def result(self):
        unanimous = set.intersection(*self.votes)
        return None if unanimous == set() else min(unanimous)
    
def findChangePts(x, threshold=0.0001, minRegime=1, minAgree=3, verbose=False):
    '''
    Apply changepoint detection method sequentially
    Inputs:
        x        : time series input
        threshold: threshold value to pass into the underlying model
        minRegime: minimum regime length (observations between changepoints) to allow
        method   : test for 'mean' or 'var'
        verbse   : print some output while using
    Outputs:
        changePts: list of detected changepoints (indices of x)
        detectPts: list of indices at which corresponding changepoints were detected
                   (a changepoint may not be detected until several observations after
                   the change)
    '''
    n = len(x)
    if n < minRegime+1:
        return [0], [0]
    
    changePts = [0] # Identified changepoints
    detectPts = [0] # When each corresponding changepoint is detected
    votes = VoteHistory(minAgree) # Require a few consecutive detections of the same changepoint
    i = 0           # Track the last detected changepoint
    j = i+1         # Consider data up to (but not including) index j
    while j <= n:
        # Find changepoints in x[i:j]
        stat = 0
        chgPts, stats = glrmean(x[i:j], threshold, minRegime)
        votes.insert(chgPts)
        chgPt = votes.result()
        if chgPt is not None:
            i += chgPt
            changePts.append(i)
            detectPts.append(j-1)
            if verbose:
                print('At idx %d, changepoint detected at idx %d' % (j-1, i))
            
            # Now that we know i is a change point, go back to i
            j = i+1
        else:
            j += 1
    return changePts, detectPts