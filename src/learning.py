import pandas as pd
import numpy as np
import matplotlib.pylab as plt
from matplotlib.pylab import rcParams
from sklearn.neural_network import MLPRegressor
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import cross_val_score
from sklearn.externals import joblib
import sys
from datetime import datetime


import csv
#https://www.analyticsvidhya.com/blog/2016/02/time-series-forecasting-codes-python/

IND_DATA_FILE = './data_utils/independent_dataset.csv'
TS_DATA_FILE = './data_utils/time_series_dataset.csv'

def read_data(file):
    x = []
    y = []
    with open(file) as datafile:
        reader = csv.reader(datafile)
        next(reader)
        for row in reader:
            x.append(row[:-1])
            y.append(row[-1])
    return x, y

def read_time_series_data(file):
    x = []
    y = []
    with open(file) as f:
        reader = csv.reader(f)
        next(reader) #Skip header
        for row in reader:
            attributes = row[0:3] + row[4:]
            y.append(row[3])
            x.append(attributes)
    return x,y
    
# NOTES:
# G and O (?) have been converted to 0 (Klaus) for regression
# P has been converted to -1 (Klaus)
def experiment_train_independent_model():
    x, y = read_data(IND_DATA_FILE)
    #x = [[1,2],[3,4],[1,3]]
    #y = [1,4,5]
    np_x = np.array(x)
    np_y = np.array(y)
    np_x = np_x.astype(np.dtype('float'))
    np_y = np_y.astype(np.dtype('float'))

    clf = MLPRegressor(verbose=True)
    print("Training")
    scores = cross_val_score(clf, np_x, np_y, cv=5, )
    print(scores)
    
    print("Training")
    clf.fit(np_x, np_y)
    joblib.dump(clf, 'independent_model_temp.pkl')

def experiment_train_time_series_model():
    x,y = read_time_series_data(TS_DATA_FILE)
    np_x = np.array(x)
    np_y = np.array(y)
    np_x = np_x.astype(np.dtype('float'))
    np_y = np_y.astype(np.dtype('float'))
    
    clf = MLPRegressor(verbose=True)
    print("Training:")
    scores = cross_val_score(clf, np_x, np_y, cv=5)
    print(scores)
    
    print("Training")
    clf.fit(np_x, np_y)
    joblib.dump(clf, 'time_series_data_model.pk1')
    
#experiment_train_independent_model()
# experiment_train_time_series_model()

######################################
# Prediction

# Read Models
try:
    ind_clf = joblib.load('src/independent_model.pkl')
    ts_clf = joblib.load('src/time_series_data_model.pk1')
except:
    print("Model not loaded")
    sys.stdout.flush()

def predict_results_independent(building_id, floor, date):
    # Convert floor to number used in regression model
    if floor == 'G' or floor == 'O':
        floor = 0
    elif floor == 'P':
        floor = -1
    elif floor == 'R':
        floor = -2

    day_of_week = date.weekday()
    hour = date.time().hour
    minute = date.time().minute

    x = [building_id, floor, day_of_week, hour, minute]
    np_x = np.array([x])
    np_x = np_x.astype(np.dtype('float'))
    return ind_clf.predict(np_x)
    
def predict_next_minute(building_id, floor, date, window):
    if floor == 'G' or floor == 'O':
        floor = 0
    elif floor == 'P':
        floor = -1
    elif floor == 'R':
        floor = -2
        
    minute = (date.day -1) * 1440 + date.hour * 60 + date.minute
    
    # x = [building_id, floor, minute]
    x = [building_id, floor]
    x.extend(window)
    np_x = np.array([x])
    np_x = np_x.astype(np.dtype('float'))
    return ts_clf.predict(np_x)
    
def get_short_term_model_accuracy(num_samples):
    #to test accuracy of short term prediction, do a random sample of 1000 points from the data, and chain predict from 1-5-10-15...-30 minutes and assess MSE at each 
    csvfile = pd.read_csv(TS_DATA_FILE)
    samples = []
    for _ in range(num_samples):
        samples.append(csvfile.sample())
    
    for sample in 
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    