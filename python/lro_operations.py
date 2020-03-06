#!/usr/bin/python3
"""list Long Running Operations (LRO)
Usually GCS catalog & event imports or purge operations

"""

import argparse
import json
import os
import sys
from apiclient.discovery import build
from pprint import pprint

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
    help='API key')
parser.add_argument(
    '--project',
    required=True,
    type=str,
    help='Cloud project #')
parser.add_argument(
    '--id',
    required=False,
    type=str,
    help='operationName, to list only a specific operation')

args = parser.parse_args()

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = args.service_account

service = build('recommendationengine',
                'v1beta1',
                discoveryServiceUrl=
                'https://recommendationengine.googleapis.com/'
                '$discovery/rest?version=v1beta1&key=' + args.apikey)

if args.id:
    request = service.projects().locations().catalogs().eventStores()\
        .operations().get(
	    name='projects/'+ args.project +
	    '/locations/global/catalogs/default_catalog'+
	    '/eventStores/default_event_store/operations/' + args.id
        )
else:
    request = service.projects().locations().catalogs().eventStores()\
        .operations().list(
            name='projects/'+ args.project +
            '/locations/global/catalogs/default_catalog'+
            '/eventStores/default_event_store',
        )

response = request.execute()

if args.id:
    pprint(response)
else:
    for operation in response['operations']:
        pprint(operation)
