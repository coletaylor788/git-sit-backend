import csv
import datetime

data_file = "output_formatted.csv"
out_file = 'out.csv'
ap_minute_counts = {} #building -> ap -> minute -> list of connection counts
floor_minute_counts = {} #building -> floor -> minute -> number of connections
#Number of connections will be determined by averaging each AP on the floor over a 10 minute range and summing over all APs on the floor

def main():
    f = open(data_file, 'r')
    reader = csv.reader(f)
    next(reader) #Need to skip the title row
    for row in reader:
      minute = getMinuteForRow(row)
    getAverageAPCountForEachMinute()
    getFloorCountsFromAPCounts()
    writeFloorCountsToFile()
    # writeMinuteCountsToFile()
    
def getMinuteForRow(row):
    building, date, connections, ap = row
    date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    microseconds_after_jan1 = date - datetime.datetime(2015,1,1,0,0,0)
    minute = round(microseconds_after_jan1.total_seconds()/60)
    if building not in ap_minute_counts:
        ap_minute_counts[building] = {}
    if ap not in ap_minute_counts[building]:
        ap_minute_counts[building][ap] = {}
    if minute not in ap_minute_counts[building][ap]:
        ap_minute_counts[building][ap][minute] = []
    ap_minute_counts[building][ap][minute].append(int(connections))


def getAverageAPCountForEachMinute():
    for building in ap_minute_counts:
        for ap in ap_minute_counts[building]:
            for minute in ap_minute_counts[building][ap]:
                ap_count_list = ap_minute_counts[building][ap][minute]
                average = float(sum(ap_count_list)/len(ap_count_list))
                ap_minute_counts[building][ap][minute] = (average, len(ap_count_list))

def getFloorCountsFromAPCounts():
    #Loop through each minute for each ap and get the average of the 10 minute range for that ap. Add this average to the count to the appropriate floor.
    for building in ap_minute_counts:
        if building not in floor_minute_counts:
            floor_minute_counts[building] = {}
        for ap in ap_minute_counts[building]:
            floor = ap[ap.find('-') + 1]
            if floor not in floor_minute_counts[building]:
                floor_minute_counts[building][floor] = {}
            for minute in range(0,43800):
                minute_range = range(minute - 6, minute + 6)
                total = 0
                sum = 0
                for range_minute in minute_range:
                    if range_minute in ap_minute_counts[building][ap]:
                        sum = sum + ap_minute_counts[building][ap][range_minute][0] * ap_minute_counts[building][ap][range_minute][1]
                        total += ap_minute_counts[building][ap][range_minute][1]
                if minute not in floor_minute_counts[building][floor]:
                    floor_minute_counts[building][floor][minute] = 0
                floor_minute_counts[building][floor][minute] += sum/total if sum != 0 else 0              
    
                
def writeFloorCountsToFile():
    f = open(out_file, 'w', newline='')
    writer = csv.writer(f)
    writer.writerow(['building','floor','minute','count'])
    for building in floor_minute_counts:
        for floor in floor_minute_counts[building]:
            for minute in floor_minute_counts[building][floor]:
                writer.writerow([building,floor,minute,floor_minute_counts[building][floor][minute]])


def write_time_series_rows(file, rows, window_size):
    f = open(file, 'w', newline='')
    writer = csv.writer(f)
    headers = ['building','floor','minute','count']
    for x in range(window_size):
        headers.append('t' + str(x))
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)

def get_window_entries(window, frequency):
    window_values = []
    for i in range(0,len(window), frequency):
        window_values.append(window[i])
    return window_values

#Window Size is the number of minutes that are kept in the window
#Window_frequency is how many minutes are between samples of the window 
#   ie Window_size = 60 with window_frequency = 5 would return 20 entries: 0, 5, 10, etc...)
def build_time_series_dataset(window_size, window_frequency, moving_average=False):
    in_file = "data_by_floor_minute.csv"
    out_file = "time_series_dataset.csv"
    f = open(in_file, 'r')
    reader = csv.reader(f)
    next(reader) #Need to skip the title row
    rows = []
    curBuilding = None
    curFloor = None
    window = [0] * window_size
    counter = window_size
    for row in reader:
        building = row[0]
        floor = row[1] = process_floor(row[1])
        occupancy = row[3]
        if building != curBuilding and curFloor != floor:
            counter = window_size
            curBuilding = building
            curFloor = floor
        else: 
            if counter != 0:
                counter -= 1
            else:
                row.extend(get_window_entries(window, window_frequency))
                rows.append(row)
        window.pop()
        window.insert(0,occupancy)
    write_time_series_rows(out_file, rows, window_size)

def build_independent_dataset():
    in_file = 'out.csv'
    out_file = 'independent_dataset.csv'
    f = open(in_file, 'r')
    reader = csv.reader(f)

    out = open(out_file, 'w', newline='')
    writer = csv.writer(out)
    writer.writerow(['building', 'floor', 'day_of_week', 'hour', 'minute', 'count'])
    
    base_date = datetime.datetime(2015, 1, 1) 
    next(reader) #Need to skip the title row
    for row in reader:
      building = row[0]
      floor = row[1] #Replace this with process_floor function? Don't want to break things so not changing it - Jake
      if floor == 'G' or floor == 'O':
        floor = 0
      if floor == 'P':
        floor = -1
      if floor == 'R':
        floor = -2
      minute = row[2]
      minute_offset = datetime.timedelta(minutes=int(minute))
      new_date = base_date + minute_offset
      day_of_week = new_date.weekday()
      time = new_date.time()  

      count = row[3]

      writer.writerow([building, floor, day_of_week, time.hour, time.minute, count])

def process_floor(floor):
    if floor == 'G' or floor == 'O':
        floor = 0
    if floor == 'P':
        floor = -1
    if floor == 'R':
        floor = -2
    return floor
      
# build_independent_dataset()
build_time_series_dataset(5,1);
