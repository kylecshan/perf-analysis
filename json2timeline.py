# Import libraries
import glob
import json
import os
import sys
import warnings
import datetime as dt
import pandas as pd

###################################################################################################
def json2timeline(files, case, np, timer, warn = True):
    '''
    Extract dates and wall-clock times (s) from ctest.json files
    '''
    # Print all warnings
    warnings.simplefilter("always")

    # Force warnings.warn() to omit the source code line in the message
    formatwarning_orig = warnings.formatwarning
    warnings.formatwarning = lambda message, category, filename, lineno, line=None: \
                formatwarning_orig(message, category, filename, lineno, line='')

    dates = []
    wtimes = []
    for file in files:
        # Load ctest data
        with open(file) as jf:
            ctestData = json.load(jf)

        # Organize data for timeline plots
        for name,info in ctestData.items():
            if info['case'] == case and info['np'] == np and info['passed']:
                if timer in info['timers']:
                    date = info['date']
                    dates.append(date)
                    wtimes.append(info['timers'][timer])
                elif warn:
                    warnings.warn(timer + ' not found in '+name+', '+file+'!', Warning)

    # Sort based on dates
    if wtimes:
        dates, wtimes = zip(*sorted(zip(dates, wtimes)))

    return dates, wtimes

###################################################################################################
def json2dataframe(files, cases, nproc, names, timers, metadata):
    output = {}
    output['case'] = []
    output['date'] = []
    for meta in metadata:
        output[meta] = []
    for name in names:
        output[name] = []
        
    for file in files:
        with open(file) as jf:
            ctestData = json.load(jf)
        
        for case in cases:
            case_nproc = case+'_np'+str(nproc)
            if case_nproc in ctestData.keys():
                info = ctestData[case_nproc]
                if not info['passed']:
                    continue
                output['case'].append(case)
                output['date'].append(dt.datetime.strptime(str(info['date']), '%Y%m%d'))
                for meta in metadata:
                    output[meta].append(info.get(meta))
                for name, timer in zip(names, timers):
                    output[name].append(info['timers'].get(timer))
                    
    return pd.DataFrame(output)



###################################################################################################
if __name__ == "__main__":
    '''
    Example: Load dummy json and test extraction of timeline data
    '''
    # Pass directory name
    if len(sys.argv) < 2:
        dir = ''
    else:
        dir = sys.argv[1]

    # Extract file names
    files = glob.glob(os.path.join(dir,'ctest-*'))

    # Specify case to extract from ctest.json file
    cases = ('ant-2-20km_ml_ls',
             'ant-2-20km_mu_ls',
             'ant-2-20km_mu_dls',
             'green-1-7km_fea_1ws',
             'green-1-7km_ml_ls_1ws',
             'green-1-7km_mu_ls_1ws',
             'green-1-7km_mu_dls_1ws',
             'green-1-7km_fea_mem',
             'green-1-7km_ml_ls_mem',
             'green-1-7km_mu_ls_mem',
             'green-1-7km_mu_dls_mem')

    # Specify number of processes to extract from ctest.json file
    np = 384

    # Specify timers to extract from ctest.json file (note: must be unique names per test in file)
    timers = ('Albany Total Time:',
              'Albany: Setup Time:',
              'Albany: Total Fill Time:',
              'Albany Fill: Residual:',
              'Albany Residual Fill: Evaluate:',
              'Albany Residual Fill: Export:',
              'Albany Fill: Jacobian:',
              'Albany Jacobian Fill: Evaluate:',
              'Albany Jacobian Fill: Export:',
              'NOX Total Preconditioner Construction:',
              'NOX Total Linear Solve:')

    # Loop over cases for this example
    for case in cases:
        for timer in timers:
            # Extract info and print
            dates, wtimes = json2timeline(files, case, np, timer)
            print(dates,wtimes)

