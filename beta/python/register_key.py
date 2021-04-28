#!/usr/bin/python3
"""Script to register an API key.
Normaly, you should only need to do this once per project.  
The registered key should be used only for predict calls 
(not exposed publicly, lik the key that may be used for event 
ingestion via the collect method)

"""

import argparse
import os
from apiclient.discovery import build

parser = argparse.ArgumentParser()
parser.add_argument(
    '--service_account',
    required=True,
    type=str,
    help='path to service account .json key file')
parser.add_argument(
    '--apikey',
    required=True,
    type=str,
    help='API key to register')
parser.add_argument(
    '--project',
    required=True,
    type=str,
    help='cloud project #')

args = parser.parse_args()

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = args.service_account

service = build('recommendationengine',
                'v1beta1',
                discoveryServiceUrl=
                'https://recommendationengine.googleapis.com/'
                '$discovery/rest?version=v1beta1&key=' + args.apikey)

json_body = {
    "predictionApiKeyRegistration": {
        'apiKey': args.apikey
    }
}

request = service.projects().locations().catalogs().eventStores()\
    .predictionApiKeyRegistrations().create(
        parent='projects/'+ args.project +
        '/locations/global/catalogs/default_catalog'+
        '/eventStores/default_event_store', body=json_body)

response = request.execute()
print(response)
