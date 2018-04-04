from sklearn.neural_network import MLPClassifier
from datetime import datetime, timedelta
import os

DEBUG = False

#DATA_FILE = 'C:\\Users\\colet\\Google Drive\\MAS\\data\\prep_data\\ml_output.csv'
CSV_DATA = os.path.abspath('C:/Users/colet/Google Drive/MAS/data/output_formatted.csv')
def build_datafile():

    data_map = {}

    with open(CSV_DATA) as infile:
        first_line = True
        line_num = 0

        # Read data into a map with times with a 1 minute interval as the key
        print("\nReading Data\n")
        for line in infile:
            if first_line:
                first_line = False
            else:
                fields = line.split(',')
                building = fields[0]
                date = datetime.strptime(fields[1], "%Y-%m-%d %H:%M:%S")
                date = date.replace(second=0) # Remove seconds from the date
                clients = int(fields[2])
                ap_name = fields[3]
                
                if date in data_map:
                    data_map[date].append([building, clients, ap_name])
                else:
                    data_map[date] = [[building, clients, ap_name]]
                
            line_num += 1
            if line_num % 10000 == 0:
                print(line_num)
            #if DEBUG and line_num >= 100:
            #    break

        # Consolidate data to get number of clients for each minute
        consolidated_data_map = {}
        line_num = 0
        print("\nConsolidate Data\n")
        for key, value in data_map.items():
            ap_clients = {}
            for entry in value:
                building = entry[0]
                ap_name = entry[2]
                clients = int(entry[1])
                if (building, ap_name) in ap_clients.keys(): # Average the values
                    ap_clients[(building, ap_name)].append(clients)
                else:
                    ap_clients[(building, ap_name)] = [clients]
    
            # Average counts of the same AP
            ap_clients_count = {}
            for (building, ap_name), client_list in ap_clients.items():
                ap_clients_count[(building, ap_name)] = int(round(sum(client_list) / len(client_list)))

            floor_map = {}

            # Generate map of building, floor -> clients
            building_floor_count = {}
            for (building, ap_name), clients in ap_clients_count.items():
                ap_floor = ap_name[ap_name.find('-') + 1]
                if (building, ap_floor) in building_floor_count:
                    building_floor_count[(building, ap_floor)] += clients
                else:
                    building_floor_count[(building, ap_floor)] = clients

            for (building, floor), clients in building_floor_count.items():
                if key in consolidated_data_map.keys():
                    consolidated_data_map[key].append([building, floor, clients])
                else:
                    consolidated_data_map[key] = [[building, floor, clients]]
            
            line_num += 1
            if line_num % 10000 == 0:
                print(line_num)
            if DEBUG and line_num >= 100:
                break
        
        # Add a moving average field to each data point
        #TODO


        #TODO Verify data accuracy by comparing to some queried data
        
        # line_num = 0
        # window_size = 10 # 10 minute window size
        # for key, value in data_map.items():
        #     include_dates = []
        #     for i in range(int(-window_size / 2), int(window_size / 2)):
        #         new_date = key + timedelta(minutes=i)
        #         include_dates.append(new_date)
                
        #     for include_date in include_dates:
        #         if include_date != key and include_date in data_map.keys():
        #             for new_data in data_map[include_date]:
        #                 data_map[key].append(new_data)

        #     line_num += 1
        #     if line_num % 10000 == 0:
        #         print(line_num)
        #     if DEBUG and line_num >= 100:
        #         break
                

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

if __name__ == '__main__':
    build_datafile()