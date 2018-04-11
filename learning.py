import pandas as pd
import numpy as np
import matplotlib.pylab as plt
from matplotlib.pylab import rcParams
from sklearn.neural_network import MLPRegressor
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import cross_val_score
from sklearn.externals import joblib


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
    #x = [[1,2],[3,4],[1,3]]
    #y = [1,4,5]
    np_x = np.array(x)
    np_y = np.array(y)
    np_x = np_x.astype(np.dtype('float'))
    np_y = np_y.astype(np.dtype('float'))

    clf = MLPRegressor(verbose=True)
    #print("Training")
    #scores = cross_val_score(clf, np_x, np_y, cv=5)
    #print(scores)
    
    print("Training")
    clf.fit(np_x, np_y)
    joblib.dump(clf, 'independent_model.pkl')
    

experiment_train_independent_model()
