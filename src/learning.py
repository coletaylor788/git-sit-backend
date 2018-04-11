import pandas as pd
import numpy as np
from sklearn.neural_network import MLPRegressor
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import KFold, cross_val_score
from sklearn.externals import joblib

import sys
from datetime import datetime
import csv

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
            y.append(row[3])
            x.append(row[0:3] + row[4:])
    return x,y

# NOTES:
# G and O (?) have been converted to 0 (Klaus) for regression
# P has been converted to -1 (Klaus)
def experiment_train_independent_model():
    x, y = read_data(IND_DATA_FILE)
    #x = [[1,2],[3,4],[1,3],[1,2],[3,4],[1,3],[1,2],[3,4],[1,3],[5,6]]
    #y = [1,4,5,1,4,5,1,4,5,6]
    np_x = np.array(x)
    np_y = np.array(y)
    np_x = np_x.astype(np.dtype('float'))
    np_y = np_y.astype(np.dtype('float'))

    clf = MLPRegressor(verbose=True)
    print("Training")
    k_fold = KFold(n_splits=5)
    scores = []
    i = 0
    for train_indices, test_indices in k_fold.split(np_x):
        model = clf.fit(np_x[train_indices], np_y[train_indices])
        score = model.score(np_x[test_indices], np_y[test_indices])
        scores.append(score)

        joblib.dump(model, 'ind_model_' + str(i) + '.pkl')

        i += 1

    with open('ind_model_cv_results.txt', 'w') as outfile:
        outfile.write(str(scores))

    #scores = cross_val_score(clf, np_x, np_y, cv=5, )
    #print(scores)
    
    #print("Training")
    #clf.fit(np_x, np_y)
    #joblib.dump(clf, 'independent_model_temp.pkl')

def experiment_train_time_series_model():
    x,y = read_time_series_data(TS_DATA_FILE)
    print(len(x))
    np_x = np.array(x)
    np_y = np.array(y)
    np_x = np_x.astype(np.dtype('float'))
    np_y = np_y.astype(np.dtype('float'))
    
    clf = MLPRegressor(verbose=True)
    print("Training")
    k_fold = KFold(n_splits=5)
    scores = []
    i = 0
    for train_indices, test_indices in k_fold.split(np_x):
        model = clf.fit(np_x[train_indices], np_y[train_indices])
        score = model.score(np_x[test_indices], np_y[test_indices])
        scores.append(score)

        joblib.dump(model, 'ts_model_' + str(i) + '.pkl')

        i += 1

    with open('ts_model_cv_results.txt', 'w') as outfile:
        outfile.write(str(scores))
        

######################################
# Prediction

# Read Models
# try:
    # ind_clf = joblib.load('src/independent_model.pkl')
    # ts_clf = joblib.load('src/time_series_data_model.pk1')
# except:
    # print("Model not loaded")
    # sys.stdout.flush()

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
    np_x = np.array(x)
    np_x = np_x.reshape(1, -1)
    np_x = np_x.astype(np.dtype('float'))
    np_y = ind_clf.predict(np_x)
    return int(np_y[0])
    
def predict_next_minute(building_id, floor, minute, window):
    # x = [building_id, floor, minute]
    x = [building_id, floor]
    x.extend(window)
    np_x = np.array([x])
    np_x = np_x.astype(np.dtype('float'))
    return ts_clf.predict(np_x)
    
def get_short_term_model_accuracy(num_samples, num_minutes):
    #to test accuracy of short term prediction, do a random sample of 1000 points from the data, and chain predict from 1-5-10-15...-30 minutes and assess MSE at each 
    csvfile = pd.read_csv(TS_DATA_FILE)
    samples = []
    error_mean_squared = [0]*num_minutes
    error_pct_off = [0]*num_minutes
    for _ in range(num_samples):
        samples.append(csvfile.sample())
    
    #TODO Rewrite this to account for the fact that predict can take in multiple x values at once
    for sample in samples:
        sample = sample.values[0]
        building = sample[0]
        floor = int(sample[1])
        minute = int(sample[2])
        window = [sample[3],sample[4],sample[5],sample[6],sample[7]]
        
        for i in range(0, num_minutes):
            next_minute_predicted = predict_next_minute(building, floor, minute + 1, window)[0]
            
            next_minute_entry = csvfile[csvfile['building'] == building][csvfile['floor'] == int(floor)][csvfile['minute'] == minute + 1]
            next_minute_actual = next_minute_entry.values[0][3]
            
            window.pop()
            window.insert(0,next_minute_predicted)
            error_mean_squared[i] += abs(next_minute_actual - next_minute_predicted)
            error_pct_off[i] += abs(next_minute_actual - next_minute_predicted) / next_minute_actual if next_minute_actual > 0 else 1
            if abs(next_minute_actual - next_minute_predicted) > 10:
                print(abs(next_minute_actual - next_minute_predicted))
                print(sample)
    return ([minute_error/num_samples for minute_error in error_mean_squared], error_pct_off)
      
# print(get_short_term_model_accuracy(1000, 10))
experiment_train_time_series_model()
# experiment_train_independent_model()
      
      
      
      
      