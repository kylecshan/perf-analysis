# Import libraries
import glob
import json
import os
import sys
import warnings
import datetime as dt
import pandas as pd

def json2dataframe(files, cases, nproc, names, timers, metadata):
    '''
    Extract timer data from json files and output as pandas DataFrame
    Inputs:
        files   : List of .json files
        cases   : List of test cases
        nproc   : Number of processes (part of case name)
        names   : Presentable names of timers
        timers  : Raw names of timers
        metadata: Additional fields to add to output
    '''
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
