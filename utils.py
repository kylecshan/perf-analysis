import datetime as dt
import matplotlib.pyplot as plt
import numpy as np

def trim(x, p, end):
    # Trim most recent observations
    if len(x) < 3:
        return x
    n = max(3, len(x)-end)
    xt = x[:n]
    # Trim most extreme observations if more than 2std away
    n_remove = int(np.floor(n*p))
    dev = np.abs(xt - xt.mean())/xt.std()
    order = np.argsort(np.abs(xt - xt.mean()))
    keep = [i for i in range(n) if dev[i] < 2 or i in order[:n-n_remove]] 
    return xt[keep]

def trimMean(x, p=.125, end=2):
    return trim(x, p, end).mean()

def trimStd(x, p=.125, end=2):
    return trim(x, p, end).std()
    
# def plotRegimes(dates, values, changePts, ax):
#     n = len(values)
#     m = len(changePts)
#     for i in range(m):
#         a = changePts[i]
#         b = changePts[i+1] if i < m-1 else n
#         regimeAvg = trimMean(values[a:b]) * np.ones(2)
#         regimeStd = trimMean(values[a:b]) * np.ones(2)
#         halfday = dt.timedelta(days=.5)
#         s = dates[a] - halfday
#         e = dates[b] - halfday if i < m-1 else dates[-1] + halfday
#         ax.axvline(x=s, color='red')
#         ax.plot([s, e], regimeAvg, color='red')
#         ax.plot([s, e], regimeAvg + 2*regimeStd, color='red', ls='--', lw=1)
#         ax.plot([s, e], regimeAvg - 2*regimeStd, color='red', ls='--', lw=1)
#         ax.plot(dates, values, color='blue')
        
def regimeTimeseries(y, changePts):
    n = len(y)
    m = len(changePts)
    mean = np.zeros_like(y)
    std = np.zeros_like(y)
    for i in range(m):
        a = changePts[i]
        b = changePts[i+1] if i < m-1 else n
        mean[a:b] = trimMean(y[a:b])
        std[a:b] = trimStd(y[a:b])
    return mean, std
        
def mergeChangePts(x):
    '''Find consecutive chunks of changepoints. Decide which one is the
    true changepoint by the mode, and break ties by taking the first.
    '''
    x = sorted(x)
    chunks = []
    tempChunk = [x[0]]
    current = x[0]
    i = 1
    while i<len(x):
        if x[i] == current or x[i] == current+1:
            tempChunk.append(x[i])
        else:
            chunks.append(tempChunk)
            tempChunk = [x[i]]
            
        current = x[i]
        i += 1
    chunks.append(tempChunk)
    
    output = []
    for chunk in chunks:
        truePt = chunk[0]
        for y in chunk:
            if chunk.count(y) > chunk.count(truePt):
                truePt = y
        output.append(truePt)
    return output
        
        
        
        
        
        
        
        
        
        