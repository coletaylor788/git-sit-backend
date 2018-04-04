import csv
import datetime

data_file = "output_formatted.csv"
out_file = 'out.csv'
minute_counts = {} #building -> ap -> minute -> list of connection counts

def main():
    f = open(data_file, 'r')
    reader = csv.reader(f)
    next(reader) #Need to skip the title row
    for row in reader:
      minute = getMinuteForRow(row)
    writeMinuteCountsToFile()
    
def getMinuteForRow(row):
    building, date, connections, ap = row
    date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    microseconds_after_jan1 = date - datetime.datetime(2015,1,1,0,0,0)
    minute = round(microseconds_after_jan1.total_seconds()/60)
    if building not in minute_counts:
        minute_counts[building] = {}
    if ap not in minute_counts[building]:
        minute_counts[building][ap] = {}
    if minute not in minute_counts[building][ap]:
        minute_counts[building][ap][minute] = []
    minute_counts[building][ap][minute].append(int(connections))
    
def writeMinuteCountsToFile():
    f = open(out_file, 'w', newline='')
    writer = csv.writer(f)
    writer.writerow(['building','ap','minute','count'])
    for building in minute_counts:
        for ap in minute_counts[building]:
            for minute in minute_counts[building][ap]:
                ap_count_list = minute_counts[building][ap][minute]
                average = float(sum(ap_count_list)/len(ap_count_list))
                writer.writerow([building,ap,minute,average])
                
                
    
main()

#Need to get building/ap/minute/occupancy
#Where minute is the average of occupancy within 30 seconds of the minute marks

#Generate dict of (building -> ap -> minute -> list of connection counts)
#Loop through dict to create (building -> ap -> minute -> average count)
#Output each entry into a file