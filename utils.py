import datetime as dt
import matplotlib.pyplot as plt
import numpy as np

def trim(x, p=.125, end=0):
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

def trimMean(x, p=.125, end=0):
    return trim(x, p, end).mean()

def trimStd(x, p=.125, end=0):
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
               
# def regimeTimeseries2(x, y, changePts):
#     n = len(y)
#     m = len(changePts)
#     newX = np.zeros(2*m)
#     mean = np.zeros(2*m)
#     std = np.zeros(2*m)
#     for i in range(m):
#         a = changePts[i]
#         b = changePts[i+1] if i < m-1 else n
#         newX[2*i], newX[2*i+1] = a, b-1
#         mean[2*i] = mean[2*i+1] = trimMean(y[a:b])
#         std[2*i] = std[2*i+1] = trimStd(y[a:b])
#     return newX, mean, std

def mergeChangePts(cps, voteThreshold=2):
    '''Given a list of list of changepoints, consolidate into a
    master set of changepoints.
    '''
    # Get max index voted for
    n = max([max(y) for y in cps]) + 1
    votes = [sum([i in cps[k] for k in range(len(cps))]) for i in range(n)]
    locks = [i for i in range(n) if votes[i] >= voteThreshold]
    rest = [i for i in range(n) 
            if votes[i] > 0
            and i not in locks
            and i+1 not in locks 
            and i-1 not in locks]
    for i in reversed(rest):
        if i-1 in rest:
            rest.remove(i)
    return sorted(locks + rest)
        
def printEvents(events, mostRecent, recency):
    '''events is a dictionary with keys that are datetime objects,
    and values which are dictionaries of (test case):(timer)
    '''
    for d in events.keys():
        c0 = None
        if mostRecent - d <= dt.timedelta(recency):
            ds = d.strftime('%m/%d/%Y')
            print(ds+':')
            for c, t in events[d].items():
                if c == c0:
                    print('    '+''.join([' ' for _ in c])+'  '+t)
                else:
                    print('    '+c+': '+t)
                c0 = c
    return {d: v for d, v in events.items() if mostRecent - d <= dt.timedelta(recency)}
        
        
        
        
        
        
        