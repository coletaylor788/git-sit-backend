import pandas as pd
import numpy as np
import matplotlib.pylab as plt
from matplotlib.pylab import rcParams
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import cross_val_score

import csv
#https://www.analyticsvidhya.com/blog/2016/02/time-series-forecasting-codes-python/

IND_DATA_FILE = './data_utils/independent_dataset.csv'

def read_data(file):
    x = []
    y = []
    with open(file) as datafile:
        reader = csv.reader(datafile)
        for row in reader:
            x.append(row[:-1])
            y.append(row[-1])
        #for line in datafile:
        #    fields = line.split(',')
        #    x.append(fields[:-1])
        #    y.append(fields[-1])
    return x, y

def experiment_train_independent_model():
    x, y = read_data(IND_DATA_FILE)
    clf = MLPRegressor()
    scores = cross_val_score(clf, x, y, cv=10)
    print(scores)
    #clf.fit(x, y)
    

experiment_train_independent_model()
