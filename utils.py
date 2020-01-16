import datetime as dt
import matplotlib.pyplot as plt
import numpy as np

# Use median absolute deviation instead of std
from scipy.stats import median_absolute_deviation as mad

def robustStd(x):
    if len(x) < 5:
        return x.std()
    else:
        return mad(x)
    
def weightedStd(priorStd, priorN, x):
    """Weighted average of a prior estimate of std and std of current sample
    """
    n = len(x)
    if n < 2:
        return priorStd
    
    std = robustStd(x)
    postStd = (priorN * priorStd + n * std) / (priorN + n)
    return postStd

def plotRegimes(dates, values, changePts, ax):
    n = len(values)
    m = len(changePts)
    for i in range(m):
        a = changePts[i]
        b = changePts[i+1] if i < m-1 else n
        regimeAvg = values[a:b].mean() * np.ones(2)
        regimeStd = robustStd(values[a:b]) * np.ones(2)
        halfday = dt.timedelta(days=.5)
        s = dates[a] - halfday
        e = dates[b] - halfday if i < m-1 else dates[-1] + halfday
        ax.axvline(x=s, color='red')
        ax.plot([s, e], regimeAvg, color='red')
        ax.plot([s, e], regimeAvg + 2*regimeStd, color='red', ls='--', lw=1)
        ax.plot([s, e], regimeAvg - 2*regimeStd, color='red', ls='--', lw=1)
        ax.plot(dates, values, color='blue')