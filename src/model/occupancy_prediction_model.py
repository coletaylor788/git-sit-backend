from sklearn.neural_network import MLPClassifier

DATA_FILE = 'C:\\Users\\colet\\Google Drive\\MAS\\data\\prep_data\\ml_output.csv'

def read_data():
    x = []
    y = []
    with open(DATA_FILE) as datafile:
        for line in datafile:
            fields = line.split(',')
            x.append(fields[:-1])
            y.append(fields[-1])
    return x, y

def train_model():
    x, y = read_data()
    for i in range(len(10)):
        print(x[i])
        print(y[i])