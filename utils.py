import datetime as dt
import matplotlib.pyplot as plt
import numpy as np

# Use median absolute deviation instead of std
from scipy.stats import median_absolute_deviation as mad

def trim(x, p=.1):
    n = len(x)
    x_s = sorted(x)
    start = int(np.floor(n*p))
    end = n-start
    return x[start:end]
    
    
def weightedStd(priorStd, priorN, x):
    """Weighted average of a prior estimate of std and std of current sample
    """
    n = len(x)
    if n < 2:
        return priorStd
    
    std = trim(x).std()
    postStd = (priorN * priorStd + n * std) / (priorN + n)
    return postStd

def plotRegimes(dates, values, changePts, ax):
    n = len(values)
    m = len(changePts)
    for i in range(m):
        a = changePts[i]
        b = changePts[i+1] if i < m-1 else n
        regimeAvg = trim(values[a:b]).mean() * np.ones(2)
        regimeStd = trim(values[a:b]).std() * np.ones(2)
        halfday = dt.timedelta(days=.5)
        s = dates[a] - halfday
        e = dates[b] - halfday if i < m-1 else dates[-1] + halfday
        ax.axvline(x=s, color='red')
        ax.plot([s, e], regimeAvg, color='red')
        ax.plot([s, e], regimeAvg + 2*regimeStd, color='red', ls='--', lw=1)
        ax.plot([s, e], regimeAvg - 2*regimeStd, color='red', ls='--', lw=1)
        ax.plot(dates, values, color='blue')
        
def regimeTimeseries(y, changePts):
    n = len(y)
    m = len(changePts)
    mean = np.zeros_like(y)
    std = np.zeros_like(y)
    for i in range(m):
        a = changePts[i]
        b = changePts[i+1] if i < m-1 else n
        mean[a:b] = trim(y[a:b]).mean()
        std[a:b] = trim(y[a:b]).std()
    return mean, std
        
        
        
        
        
        
        
        
        
        
        