import os
import flask as Flask
from flask_cors import CORS
import psycopg2 as dbTool
import random
import datetime 
from functools import reduce
from src.db_tools import *

OCCUPANCY_WINDOW = 300 #Milliseconds to each side of the time to get occupancy from

app = Flask.Flask(__name__, static_url_path='')
CORS(app)

db = connect_to_database()

def get_clients_around_date_by_building_floor(building, floor, date):
    lower_date = date + datetime.timedelta(0,-1 * OCCUPANCY_WINDOW)
    upper_date = date + datetime.timedelta(0,OCCUPANCY_WINDOW)
    entries = db.child(building).get().val()
    
    in_range_items = []
    for key, value in entries.items():
       item_date = datetime.datetime.strptime(key, '%b %d %H:%M:%S %Y')
       if item_date >= lower_date and item_date <= upper_date:
           in_range_items.append(value)

    record_count = 0
    client_count = 0
    for item in in_range_items:
        ap_floor = item[1][0] # Note both floor and ap_floor are strings
        if ap_floor == floor:
            client_count += item[0]
            record_count += 1

    return 0 if record_count == 0 else int(round(client_count / record_count))

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
    
"""
Main method starts the Flask server
"""
if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

    #TESTING ONLY! Leave commented in production
    #app.run(host='127.0.0.1', port=port)
   