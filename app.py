import os
import flask as Flask
from flask_cors import CORS
import psycopg2 as dbTool
import random
import datetime 
from functools import reduce
from src.db_tools import *

import db

OCCUPANCY_WINDOW = 300 #Milliseconds to each side of the time to get occupancy from

app = Flask.Flask(__name__, static_url_path='')
CORS(app)

#ONLY HAVE THIS IN TESTING
#conn=dbTool.connect(dbname="postgres", user="postgres", password="happywonder")

#ONLY HAVE THIS IN PROD
# DATABASE_URL = os.environ['DATABASE_URL']
# conn = dbTool.connect(DATABASE_URL, sslmode='require')

db = connect_to_database()

def getClientsAroundDateByAP(building, date):
    lowerDate = date + datetime.timedelta(0,-1 * OCCUPANCY_WINDOW)
    upperDate = date + datetime.timedelta(0,OCCUPANCY_WINDOW)
    return "SELECT avg(clients) FROM occupancy where building='" + building + "' AND date > '" + str(lowerDate) + "' AND date < '" + str(upperDate) + "' GROUP BY ap_name"

def getMappedDate(date):
    date = date.replace(year=2015, month=1)
    if date.day > 30:
        date = date.replace(day=31)
    return date
    
@app.route('/')
def hello():
    return 'Hello World!'
    
@app.route('/testDB', methods=["GET"])
def testDB():
    pg = db.executeReadQuery("SELECT * FROM occupancy", conn)
    sample = pg[0]
    return str(sample)

@app.route('/get-current-occupancy', methods=["POST"])
def get_current_occupancy():
    building_id = Flask.request.get_json()['location-id']
    date = getMappedDate(datetime.datetime.now())
    q = getClientsAroundDateByAP(building_id, date)
    results = db.executeReadQuery(q , conn)
    print(results)
    occ = sum(reduce((lambda x,y: x + y), results))
    return "{'occupancy': " + str(occ) + "}"
    
@app.route('/get-occupancy-date', methods=["POST"])
def get_occupancy_date():
    building_id = Flask.request.get_json()['location-id']
    date = Flask.request.get_json()['datetime']
    date = getMappedDate(datetime.datetime.strptime(date, "%Y-%m-%d %X"))
    q = getClientsAroundDateByAP(building_id, date)
    results = db.executeReadQuery(q , conn)
    print(results)
    occ = sum(reduce((lambda x,y: x + y), results))
    return "{'occupancy': " + str(occ) + "}"
    
"""
Main method starts the Flask server
"""
if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    # app.run(host='0.0.0.0', port=port)

    #TESTING ONLY! Leave commented in production
    app.run(host='127.0.0.1', port=port)
   