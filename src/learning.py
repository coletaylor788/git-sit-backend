import pandas as pd
import numpy as np
#import matplotlib.pylab as plt
#from matplotlib.pylab import rcParams

from sklearn.neural_network import MLPRegressor
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import KFold, cross_val_score
from sklearn.externals import joblib

import sys


import csv
#https://www.analyticsvidhya.com/blog/2016/02/time-series-forecasting-codes-python/

IND_DATA_FILE = './data_utils/independent_dataset.csv'

def read_data(file):
    x = []
    y = []
    with open(file) as datafile:
        reader = csv.reader(datafile)
        next(reader)
        for row in reader:
            x.append(row[:-1])
            y.append(row[-1])
        #for line in datafile:
        #    fields = line.split(',')
        #    x.append(fields[:-1])
        #    y.append(fields[-1])
    return x, y

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

#experiment_train_independent_model()

######################################
# Prediction

# Read Models
try:
    ind_clf = joblib.load('src/independent_model.pkl')
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
    np_x = np.array(x)
    np_x = np_x.reshape(1, -1)
    np_x = np_x.astype(np.dtype('float'))
    np_y = ind_clf.predict(np_x)
    return int(np_y[0])
