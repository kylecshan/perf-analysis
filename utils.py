import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import warnings
from IPython.display import HTML, clear_output
        
def print_events(events, most_recent, recency):
    '''events is a dictionary with keys that are datetime objects,
    and values which are dictionaries of (test case):(timer)
    '''
    for date in events.keys():
        if most_recent - date <= dt.timedelta(recency):
            datestr = date.strftime('%m/%d/%Y')
            print(datestr+':')
            for case, names in events[date].items():
                first_name = True
                for name in names:
                    if first_name:
                        print('    '+case+': '+name)
                    else:
                        print('    '+''.join([' ' for _ in case])+'  '+name)
                    first_name = False
    return {d: v for d, v in events.items() if most_recent - d <= dt.timedelta(recency)}
        
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

def check_config(config):
    fields = ('threshold', 'recency', 'json_regex', 'metadata', 'cases', 'names', 'timers')
    missing = []
    for field in fields:
        if field not in config.keys():
            missing.append(field)
    if len(missing) > 0:
        raise KeyError('Config file missing fields: ' + str(missing))
        
    extra = []
    for field in config.keys():
        if field not in fields:
            extra.append(field)
    if len(extra) > 0:
        warnings.warn('Extraneous config fields: ' + str(extra))
    return
        
def make_numpy(*args):
    if len(args) == 1:
        return np.asarray(args[0])
    else:
        return tuple(np.asarray(x) for x in args)
        
        