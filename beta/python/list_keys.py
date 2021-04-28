#!/usr/bin/python3
"""Script to list registered API keys

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
    help='API key to remove')
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

request = service.projects().locations().catalogs().eventStores()\
    .predictionApiKeyRegistrations().list(
        parent='projects/'+ args.project +
        '/locations/global/catalogs/default_catalog'+
        '/eventStores/default_event_store'
    )

response = request.execute()
for key in response['predictionApiKeyRegistrations']:
    print(key)
