import os
import flask as Flask
from flask_cors import CORS
import psycopg2 as dbTool
import random
import datetime 
from functools import reduce

import db

app = Flask.Flask(__name__, static_url_path='')
CORS(app)

#ONLY HAVE THIS IN TESTING
# conn=dbTool.connect(dbname="postgres", user="postgres", password="happywonder")

#ONLY HAVE THIS IN PROD
DATABASE_URL = os.environ['DATABASE_URL']
conn = dbTool.connect(DATABASE_URL, sslmode='require')

def getClientsWithinDateRangeByAP(building, lowerDate, upperDate):
    return "SELECT avg(clients) FROM occupancy where building=" + building + " AND date > '" + str(lowerDate) + "' AND date < '" + str(upperDate) + "' GROUP BY ap_name"

# Test endpoint
@app.route('/')
def hello():
    return 'Hello World!'
    
@app.route('/testDB', methods=["GET"])
def testDB():
    pg = db.executeReadQuery("SELECT * FROM test", conn)
    sample = pg[0]
    return str(sample)

@app.route('/get-current-occupancy', methods=["POST"])
def get_current_occupancy():
    building_id = Flask.request.get_json()['location-id']
    date = datetime.datetime.now()
    lower = date + datetime.timedelta(0,-300)
    upper = date + datetime.timedelta(0,300)
    q = getClientsWithinDateRangeByAP(building_id, lower, upper)
    results = db.executeReadQuery(q , conn)
    print(results)
    sum = reduce((lambda x,y: x[0] + y[0]), results)
    averageClientCount = sum/len(results)
    # return "{occupancy: " + str(random.random()) + "}"
    return "{'occupancy': " + str(averageClientCount) + "}"
    
"""
Main method starts the Flask server
"""
if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

    #TESTING ONLY! Leave commented in production
    # app.run(host='127.0.0.1', port=port)
   