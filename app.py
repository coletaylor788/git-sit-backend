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

    # Convert to format in database
    lower_date_str = lower_date.strftime("%b %d %H:%M:%S %Y")
    upper_date_str = upper_date.strftime("%b %d %H:%M:%S %Y")

    entries = db.child(building).order_by_key().start_at(lower_date_str).end_at(upper_date_str).get().val()

    # Consolidate into map from AP to clients
    ap_clients = {}
    for _, value in entries.items():
        ap_name = value[1]
        ap_floor = ap_name[ap_name.find('-') + 1]
        clients = int(value[0])
        if ap_floor == floor:
            if ap_name in ap_clients.keys(): # Average the values
                ap_clients[ap_name].append(clients)
            else:
                ap_clients[ap_name] = [clients]
    
    # Average counts of the same AP
    ap_clients_count = {}
    for ap_name, client_list in ap_clients.items():
        ap_clients_count[ap_name] = int(round(sum(client_list) / len(client_list)))

    return 0 if len(ap_clients_count.values()) == 0 else sum(ap_clients_count.values())

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
   