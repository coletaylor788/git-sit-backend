import os
import flask as Flask
from flask_cors import CORS
import random

app = Flask.Flask(__name__, static_url_path='')
CORS(app)

# Test endpoint
@app.route('/')
def hello():
    return 'Hello World!'


@app.route('/get-current-occupancy', methods=["POST"])
def get_current_occupancy():
    if Flask.request.method == "POST":
        building_id = Flask.request.values.get('schedule')
        return "{occupancy: " + str(random.random()) + "}"

"""
Main method starts the Flask server
"""
if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

    #TESTING ONLY! Leave commented in production
    #app.run(host='127.0.0.1', port=port)