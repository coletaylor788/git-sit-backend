import csv

in_file = "ML Data.csv"
out_file = "ML_Time_Series.csv"

def add_time_series(window_size):
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
        floor = row[1]
        occupancy = row[3]
        if building != curBuilding and curFloor != floor:
            counter = window_size
            curBuilding = building
            curFloor = floor
        else: 
            if counter != 0:
                counter -= 1
            else:
                row.extend(window)
                rows.append(row)
        window.pop()
        window.insert(0,occupancy)
    writeRowsToFile(rows, window_size)
    
def writeRowsToFile(rows, window_size):
    f = open(out_file, 'w', newline='')
    writer = csv.writer(f)
    headers = ['building','floor','minute','count']
    for x in range(window_size):
        headers.append('t' + str('x'))
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)
        
add_time_series(5)