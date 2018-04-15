import os
import flask as Flask
from flask_cors import CORS
import psycopg2 as dbTool
import random
import datetime 
from functools import reduce
from src.db_tools import *
from src.learning import *
import json
import sys

OCCUPANCY_WINDOW = 300 #Seconds to each side of the time to get occupancy from
LONG_MODEL_START_TIME = datetime.timedelta(minutes=123)

app = Flask.Flask(__name__, static_url_path='')
CORS(app)

db = connect_to_database()

import sys
def get_clients_around_date_by_building_floor(building, floor, date):
    lower_date = date + datetime.timedelta(0,-1 * OCCUPANCY_WINDOW)
    upper_date = date + datetime.timedelta(0,OCCUPANCY_WINDOW)

    # Convert to format in database
    lower_date_str = lower_date.strftime("%b %d %H:%M:%S %Y")
    if lower_date_str[4] == '0':
        lower_date_str = lower_date_str[:4] + lower_date_str[4 + 1:]
    upper_date_str = upper_date.strftime("%b %d %H:%M:%S %Y")
    if upper_date_str[4] == '0':
        upper_date_str = upper_date_str[:4] + upper_date_str[4 + 1:]
    
    entries = db.child(building).order_by_key().start_at(lower_date_str).end_at(upper_date_str).get().val()
    #TODO Calling .val on the query above throws an exception if no data is found
    # Should gracefully handle this

    # Consolidate into map from AP to clients
    ap_clients = {}
    for _, value in entries.items():
        ap_name = value[1]
        ap_floor = ap_name[ap_name.find('-') + 1]
        clients = int(value[0])
        if ap_floor == str(floor):
            if ap_name in ap_clients.keys(): # Average the values
                ap_clients[ap_name].append(clients)
            else:
                ap_clients[ap_name] = [clients]

    # Average counts of the same AP
    ap_clients_count = {}
    for ap_name, client_list in ap_clients.items():
        ap_clients_count[ap_name] = round(sum(client_list) / len(client_list))

    return 0 if len(ap_clients_count.values()) == 0 else int(sum(ap_clients_count.values()))

def get_historical_data_from_firebase(building, floor, start, end):
    occ_map = {}
    lower_date_str = start.strftime("%b %d %H:%M:%S %Y")
    if lower_date_str[4] == '0':
        lower_date_str = lower_date_str[:4] + lower_date_str[4 + 1:]
    end = end if end < datetime.datetime.now() else datetime.datetime.now()
    end = getMappedDate(end)
    upper_date_str = end.strftime("%b %d %H:%M:%S %Y")
    if upper_date_str[4] == '0':
        upper_date_str = upper_date_str[:4] + upper_date_str[4 + 1:]
        
    print(lower_date_str, file=sys.stderr)
    print(upper_date_str, file=sys.stderr)
        
    x = str(datetime.datetime.now())
    print(x, file=sys.stderr)
    entries = db.child(building).order_by_key().start_at(lower_date_str).end_at(upper_date_str).get()
    y = str(datetime.datetime.now())
    print(y, file=sys.stderr)
    
    for entry in entries.each():
        # print(str(entry), file=sys.stderr)
        date = entry.key()
        date = datetime.datetime.strptime(date, "%b %d %H:%M:%S %Y")
        client_count = int(entry.val()[0])
        ap_name = entry.val()[1]
        ap_floor = ap_name[ap_name.find('-') + 1]
        if ap_floor == str(floor):
            occ_map[date.strftime("%Y-%m-%d %H:%M:%S")] = client_count
            
    return occ_map
        
def get_clients_over_time_by_building_floor(building, floor, start_date, end_date, interval = datetime.timedelta(minutes=1)):
    occ_map = {}
    str_occ_map = {}
    curr_date = getMappedDate(datetime.datetime.now())
    iter_date = start_date
    last_valid_count = 0 # Used if data doesn't exist for a particular time
    
    #TODO make this get the list of occupancies for short term prediction all at once instead of calling 1, 2, 3, 4, .... LONG_MODEL_START_TIME
    while iter_date <= end_date:
        occ = last_valid_count
        
        if iter_date >= curr_date and end_date < curr_date + LONG_MODEL_START_TIME: #If end date is before we start using the long term model
            window = []
            for i in range(0,5):
              window.append(get_clients_around_date_by_building_floor(building, floor, iter_date - datetime.timedelta(minutes=i)))
            occList = predict_time_series_minute(building, floor, curr_date, end_date, window)
            
            x = 0
            while iter_date <= end_date:
                str_occ_map[iter_date.strftime("%Y-%m-%d %H:%M:%S")] = occList[x]
                iter_date += datetime.timedelta(minutes=1)
                x += 1;
            iter_date = end_date
        elif iter_date <= curr_date: # Query
            occ = get_clients_around_date_by_building_floor(building, floor, iter_date)
            iter_date += interval
        else: # Predict
            if iter_date < curr_date + LONG_MODEL_START_TIME:
                #Get window
                window = []
                for i in range(0,5):
                  window.append(get_clients_around_date_by_building_floor(building, floor, iter_date - datetime.timedelta(minutes=i)))
                occList = predict_time_series_minute(building, floor, curr_date, curr_date + LONG_MODEL_START_TIME, window)
                x = 0
                # print(str_occ_map, file=sys.stderr)
                while iter_date <= curr_date + LONG_MODEL_START_TIME:
                    str_occ_map[iter_date.strftime("%Y-%m-%d %H:%M:%S")] = occList[x]
                    iter_date += datetime.timedelta(minutes=1)
                    x += 1;
                iter_date = curr_date + LONG_MODEL_START_TIME
            else:
                occ = predict_results_independent(building, floor, iter_date)
            iter_date += datetime.timedelta(minutes = 1)
        
        str_occ_map[iter_date.strftime("%Y-%m-%d %H:%M:%S")] = occ
        
        iter_date += datetime.timedelta(minutes = 1)
        last_valid_count = occ
        
    
    return str_occ_map

def getMappedDate(date):
    date = date.replace(year=2015, month=1)
    if date.day > 30:
        date = date.replace(day=30)
    return date

@app.route('/')
def hello():
    return 'Hello World!'

@app.route('/get-current-occupancy', methods=["POST"])
def get_current_occupancy():
    building_id = Flask.request.get_json()['location-id']
    floor = Flask.request.get_json()['floor']
    date = getMappedDate(datetime.datetime.now())
    
    occ = get_clients_around_date_by_building_floor(building_id, floor, date)
    return "{'occupancy': " + str(occ) + "}"
    
@app.route('/get-occupancy-date', methods=["POST"])
def get_occupancy_date():
    building_id = Flask.request.get_json()['location-id']
    floor = Flask.request.get_json()['floor']
    date = Flask.request.get_json()['datetime']
    date = getMappedDate(datetime.datetime.strptime(date, "%Y-%m-%d %X"))
    
    occ = get_clients_around_date_by_building_floor(building_id, floor, date)
    return "{'occupancy': " + str(occ) + "}"
    
@app.route('/get-next-week-occupancy', methods=["POST"])
def get_next_week_occupancy():
    building_id = Flask.request.get_json()['location-id']
    floor = Flask.request.get_json()['floor']
    curr_date = getMappedDate(datetime.datetime.now())
    curr_date = curr_date.replace(second=0,microsecond=0)
    end_date = curr_date + datetime.timedelta(days=7)
    interval = datetime.timedelta(hours=1)
        
    occ_map = get_clients_over_time_by_building_floor(building_id, floor, curr_date, end_date)
    occ_map = get_clients_over_interval_from_occ_map(occ_map, interval)
    
    return json.dumps(occ_map)

@app.route('/get-next-day-occupancy', methods=["POST"])
def get_next_day_occupancy():
    building_id = Flask.request.get_json()['location-id']
    floor = Flask.request.get_json()['floor']
    curr_date = getMappedDate(datetime.datetime.now())
    curr_date = curr_date.replace(second=0,microsecond=0)
    end_date = curr_date + datetime.timedelta(days=1)
    interval = datetime.timedelta(minutes=30)

    occ_map = get_clients_over_time_by_building_floor(building_id, floor, curr_date, end_date)
    occ_map = get_clients_over_interval_from_occ_map(occ_map, interval)

    
    return json.dumps(occ_map)

@app.route('/get-next-hour-occupancy', methods=["POST"])
def get_next_hour_occupancy():
    building_id = Flask.request.get_json()['location-id']
    floor = Flask.request.get_json()['floor']
    curr_date = getMappedDate(datetime.datetime.now())
    curr_date = curr_date.replace(second=0,microsecond=0)
    end_date = curr_date + datetime.timedelta(hours=1)
    interval = datetime.timedelta(minutes=1)

    occ_map2 = get_clients_over_time_by_building_floor(building_id, floor, curr_date, end_date)
    occ_map3 = get_clients_over_interval_from_occ_map(occ_map2, interval)
    
    return json.dumps(occ_map3)

@app.route('/get-last-week-occupancy', methods=["POST"])
def get_last_week_occupancy():
    building_id = Flask.request.get_json()['location-id']
    floor = Flask.request.get_json()['floor']
    curr_date = getMappedDate(datetime.datetime.now())
    curr_date = curr_date.replace(second=0,microsecond=0)
    start_date = curr_date - datetime.timedelta(days=1)
    interval = datetime.timedelta(hours=6)

    # occ_map = get_clients_over_time_by_building_floor(building_id, floor, start_date, curr_date, interval)
    # occ_map = get_clients_over_interval_from_occ_map(occ_map, interval)
    
    occ_map = get_historical_data_from_firebase(building_id, floor, start_date, curr_date)
    occ_map = get_clients_over_interval_from_occ_map(occ_map, interval)
    
    return json.dumps(occ_map)

@app.route('/get-last-day-occupancy', methods=["POST"])
def get_last_day_occupancy():
    building_id = Flask.request.get_json()['location-id']
    floor = Flask.request.get_json()['floor']
    curr_date = getMappedDate(datetime.datetime.now())
    curr_date = curr_date.replace(second=0,microsecond=0)
    start_date = curr_date - datetime.timedelta(days=1)
    interval = datetime.timedelta(minutes=30)

    occ_map = get_historical_data_from_firebase(building_id, floor, start_date, curr_date)
    occ_map = get_clients_over_interval_from_occ_map(occ_map, interval)
    
    return json.dumps(occ_map)

@app.route('/get-last-hour-occupancy', methods=["POST"])
def get_last_hour_occupancy():
    building_id = Flask.request.get_json()['location-id']
    floor = Flask.request.get_json()['floor']
    curr_date = getMappedDate(datetime.datetime.now())
    curr_date = curr_date.replace(second=0,microsecond=0)
    start_date = curr_date - datetime.timedelta(hours=1)
    interval = datetime.timedelta(minutes=1)

    occ_map = get_historical_data_from_firebase(building_id, floor, start_date, curr_date)
    occ_map = get_clients_over_interval_from_occ_map(occ_map, interval)
    
    return json.dumps(occ_map)

def get_clients_over_interval_from_occ_map(occ_map, interval):
    interval_occ_map = {}
    occ_map = {datetime.datetime.strptime(dt, "%Y-%m-%d %H:%M:%S"): val for (dt, val) in occ_map.items()}
    for date in occ_map:
        occupancy = occ_map[date]
        date = roundTime(date, interval.total_seconds())
        if date not in interval_occ_map:
            interval_occ_map[str(date)] = []
        interval_occ_map[str(date)].append(occupancy)
        
    interval_occ_map = {dt: sum(occupancy)/len(occupancy) for (dt, occupancy) in interval_occ_map.items()}
    
    return interval_occ_map

def roundTime(dt=None, roundTo=60):
   """Round a datetime object to any time laps in seconds
   dt : datetime.datetime object, default now.
   roundTo : Closest number of seconds to round to, default 1 minute.
   """
   if dt == None : dt = datetime.datetime.now()
   seconds = (dt.replace(tzinfo=None) - dt.min).seconds
   rounding = (seconds+roundTo/2) // roundTo * roundTo
   return dt + datetime.timedelta(0,rounding-seconds,-dt.microsecond)
    
"""
Main method starts the Flask server
"""
if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

    #TESTING ONLY! Leave commented in production
    # app.run(host='127.0.0.1', port=port)
   