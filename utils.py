import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
from IPython.display import HTML

def trim(x, p=.125, end=0):
    '''
    Remove observations that may be outliers - suspiciously far from the average.
    At most [floor(len(x)*p) + end] points are removed.
    Inputs:
        x  : data to trim
        p  : proportion of data to remove
        end: number of data points at the end of x to ignore
    '''
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

               
def mergeChangePts(cps, voteThreshold=2):
    '''Given a list of list of changepoints, consolidate into a
    master set of changepoints. First, keep changepoints that multiple lists
    agree on. Of the remaining, for each group of consecutive changepoints, pick
    the earliest one. Output will have no consecutive changepoints.
    Input:
        cps          : list of lists of detected changepoints
        voteThreshold: number of lists that must agree for a changepoint to be
                         automatically voted in
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
        
# https://stackoverflow.com/questions/27934885/how-to-hide-code-from-cells-in-ipython-notebook-visualized-with-nbviewer
def hide_code_button():
    '''
    Create an HTML button that hides all code blocks in a jupyter notebook
    '''
    return HTML('''
        <script>
        code_show=true; 
        function code_toggle() {
         if (code_show){
         $('div.input').hide();
         } else {
         $('div.input').show();
         }
         code_show = !code_show
        } 
        $( document ).ready(code_toggle);
        </script>
        <form action="javascript:code_toggle()">
        <input type="submit" value="Show/hide code blocks">
        </form>
    ''')        

        
        
        
        