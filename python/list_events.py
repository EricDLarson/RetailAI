#!/usr/bin/python3
"""List all Recommendations AI User Events for a given time period.

Returns one json response per line
This is useful for importing into BigQuery or other offline analysis:
https://cloud.google.com/bigquery/docs/loading-data-cloud-storage-json
"""

import argparse
import json
from apiclient.discovery import build
from google.oauth2 import service_account

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
    help='cloud project #')
parser.add_argument(
    '--start_date',
    required=False,
    type=str,
    help='Start Date: YYYY-MM-DD')
parser.add_argument(
    '--end_date',
    required=False,
    type=str,
    help='End Date: YYYY-MM-DD')
parser.add_argument(
    '--event_type',
    required=False,
    type=str,
    help='deteail-page-view, add-to-cart, purchase-complete, etc')
parser.add_argument(
    '--events_missing_catalog_items',
    required=False,
    action='store_true',
    help='Return only unjoined events')

args = parser.parse_args()

filter_string = ''
if args.start_date is not None:
  filter_string = (' eventTime > "' + args.start_date + 'T00:00:00.00Z" ')
if args.end_date is not None:
  filter_string = (filter_string + ' eventTime < "' +
                   args.end_date + 'T23:59:59.99Z" ')
if args.event_type is not None:
  filter_string = (filter_string + ' eventType = '+ args.event_type)
if args.events_missing_catalog_items:
  filter_string = (filter_string + ' eventsMissingCatalogItems')


SCOPES = ['https://www.googleapis.com/auth/cloud-platform']
SERVICE_ACCOUNT_FILE = args.service_account
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Can also set GOOGLE_APPLICATION_CREDENTIALS environment variable,
# But the above creditals code may be somewhat more "correct"
# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = args.service_account

service = build('recommendationengine',
                'v1beta1',
                discoveryServiceUrl=
                'https://recommendationengine.googleapis.com/'
                '$discovery/rest?version=v1beta1&key=' + args.apikey,
                credentials=credentials
               )

next_page = ''
while next_page is not None:

  request = service.projects().locations().catalogs().eventStores()\
      .userEvents().list(
          parent='projects/'+ args.project +
          '/locations/global/catalogs/default_catalog'+
          '/eventStores/default_event_store',
          filter=filter_string,
          pageSize=5000, pageToken=next_page)

  response = request.execute()

  if 'nextPageToken' in response:
    next_page = response['nextPageToken']
  else:
    next_page = None

  try:
    for event in response['userEvents']:
      try:  # Add currencyCode since it's not returned currently (b/130748472)
        for i in range(len(event['productEventDetail']['productDetails'])):
          event['productEventDetail']['productDetails'][i]['currencyCode'] = (
              'USD')
      except KeyError:
        pass
      print(json.dumps(event))
  except KeyError:
    pass
