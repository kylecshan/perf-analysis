# perf-analysis
This repo contains Kyle's code for his ICME Xplore project with Sandia.

The purpose of this project is to detect changes in the performance of ice sheet simulations. We use generalized likelihood methods to identify change points, and overlay them on a graph of historical run times. See Changepoint_Interactive.html for an example.

## Code organization
* basicstats.py – outlier removal, basic statistical tests such as t-test, summary statistics
* email_report.py – perform changepoint analysis on single timeseries for email report
* json2timeline.py – collect data from json files
* models.py – changepoint detection model
* plotutils.py – tools for Plotly figures
* utils.py – miscellaneous functions
* Changepoint_Interactive.ipynb – analyze time series independently
* Comparison_Interactive.ipynb – analyze two test cases side-by-side
* EmailReportExample.ipynb – quick demonstration of email_report output
* UpdateTestNames.ipynb – update old test names (in .json files) with new test names

## Notebook configuration settings
The main notebooks are Changepoint_Interactive and Comparison_Interactive. Both load various settings from config.json, which are also verified by check_config in utils.py:
* threshold – roughly the significance level of the model. If the data followed all distribution assumptions (i.i.d. lognormal observations with occasional shifts in the log mean), this would be an upper bound on the false discovery rate. Values from 0.01 to 0.0001 could be reasonable, depending on the desired sensitivity of the model.
* recency – controls the lookback window for recent changepoint discoveries which are printed to the notebooks. Measured in actual days since the most recent observation.
* json_regex – regular expression matching the location of json files.
* metadata – fields in the json file that might be desirable for hover-text information. Current implementation assumes that these will be in the order [compiler, Albany commit, Trilinos commit].
* cases – test cases, including number of processes, e.g. ant-2-20km_ml_ls_np384
* names – display names of timers. Elements should be in 1-1 correspondence with actual timer names.
* timers – actual names of the timers in json files.

## Changepoint model parameters
It may make sense to add these parameters to the config file at some point.
* alpha – significance level of the model; currently the only parameter being set in config.json. A higher value will make the model more sensitive.
* min_agree – minimum number of consecutive detections of the same changepoint before it is marked as a changepoint. A higher value will make the model less sensitive, and increase the minimum time to detection.
* num_test – each time we test for a possible changepoint, we consider this many of the largest jumps in the time series as candidate changepoints. Increasing this value will make the model less sensitive and find changepoints more precisely, but increases runtime.
* lookback – only consider a maximum trailing window of this many observations. Increasing this value will make the model more sensitive when sample sizes are large.

## Changepoint_Interactive pipeline
* Load config.json and verify that it has the correct fields
* Load data from json files into a pandas DataFrame. Required fields are:
o	date – as python datetime.datetime object
o	Metadata fields – strings 
o	case – test case name; string
o	Timer names – numeric for each timer name in “names” (not “timers”)
* Find changepoints
o	For each test case + timer, take subset of the DataFrame with the given case, and timers are not NA
o	Apply log transformation to timers
o	Apply changepoint detection model, parallelized over timers using the python multiprocessing package
o	Calculate mean and standard deviation of each case + timer between consecutive changepoints
* Plot (de-logged) time series and mean/std trends in interactive chart. 

## Comparison_Interactive pipeline
* Load config.json and verify that it has the correct fields
* Load data from json files into a pandas DataFrame. Required fields are:
o	date – as python datetime.datetime object
o	Metadata fields – strings 
o	case – test case name; string
o	Timer names – numeric for each timer name in “names” (not “timers”)
* Find changepoints
o	For each test case + timer, take subset of the DataFrame with the given case, and timers are not NA
o	Apply log transformation to timers
o	Apply changepoint detection model, parallelized over timers using the python multiprocessing package
o	Calculate mean of each case + timer between consecutive changepoints
* Plot (de-logged) time series and mean trends for a pair of test cases in interactive chart
* Join two time series to return observations on dates where neither test failed, and take the difference of the log-transformed series. Apply changepoint detection model to time series of difference of logs.
* Plot (de-logged) time series and mean/std trends for the difference. In this case, de-logged converts log differences to relative (percentage) differences.
* Plot (de-logged) histogram of the difference since the latest changepoint
* Compute and print summary statistics and t-test of the average time difference
* Define interactive update rules for drop-down menus, and display charts

## Package Information
This repository uses the following versions of select packages:
* python 3.7.6
* numpy 1.17.3
* pandas 0.25.3
* plotly 4.5.0
* scipy 1.3.1
* ipython 7.11.1
* ipywidgets 7.5.1
* multiprocess 0.70.9