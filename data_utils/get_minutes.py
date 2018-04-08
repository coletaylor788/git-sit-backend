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

main()
