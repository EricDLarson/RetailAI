#!/usr/bin/python3
"""Import catalog from a GCS bucket
https://cloud.google.com/recommendations-ai/docs/reference/rest/v1beta1/projects.locations.catalogs.catalogItems/import

You will need to customize the json_body below for your GCS bucket paths

"""

import argparse
import json
import os
import sys
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
    help='API key')
parser.add_argument(
    '--project',
    required=True,
    type=str,
    help='Cloud project #')

args = parser.parse_args()

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = args.service_account

service = build('recommendationengine',
                'v1beta1',
                discoveryServiceUrl=
                'https://recommendationengine.googleapis.com/'
                '$discovery/rest?version=v1beta1&key=' + args.apikey)

# Customize to your environment
#https://cloud.google.com/recommendations-ai/docs/reference/rest/v1beta1/InputConfig#GcsSource
json_body = {
  "requestId": 'import12345', # Optional
  "inputConfig": {
    "gcsSource": {
      # Note you can use * for all files in bucket, or pass a list of bucket/files
      "inputUris": ['gs://mybucket/*']
    },
  },
  "errorsConfig": {
      "gcsPrefix": 'gs://mybucket/errors'
  }
}

import_request = service.projects().locations().catalogs().eventStores()\
    .catalogItems().import_(
        parent='projects/'+ args.project +
        '/locations/global/catalogs/default_catalog'+
        '/eventStores/default_event_store',
        body=json_body
    )

response = import_request.execute()
print(response)

