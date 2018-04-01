import pyrebase
from os import environ
import json

def connect_to_database():

    # Must read from environment variables for security
    auth_dict = {}
    auth_dict['type'] = environ.get('type')
    auth_dict['project_id'] = environ.get('project_id')
    auth_dict['private_key_id'] = environ.get('private_key_id')
    auth_dict['private_key'] = environ.get('private_key')
    auth_dict['client_email'] = environ.get('client_email')
    auth_dict['client_id'] = environ.get('client_id')
    auth_dict['auth_uri'] = environ.get('auth_uri')
    auth_dict['token_uri'] = environ.get('token_uri')
    auth_dict['auth_provider_x509_cert_url'] = environ.get('auth_provider_x509_cert_url')
    auth_dict['client_x509_cert_url'] = environ.get('client_x509_cert_url')

    with open('temp_auth.json', 'w') as outfile:
        json.dump(auth_dict, outfile)

    with open('temp_auth.json') as infile:
        outfile = open("auth.json", "w")

        output = ""
        for line in infile:
            output += line

        output = output.replace('\\n', 'n')
        outfile.write(output)
        outfile.close()


    config = {
        "apiKey": "AIzaSyCqni7VJ5DjbQDidU7BPfOAZdcsvPWwcu8 ",
        "authDomain": "git-sit.firebaseapp.com",
        "databaseURL": "https://git-sit.firebaseio.com",
        "storageBucket": "git-sit.appspot.com",
        "serviceAccount": "./auth.json"
    }

    firebase = pyrebase.initialize_app(config)
    db = firebase.database()

    return db

