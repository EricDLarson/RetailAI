#!/usr/bin/python3
"""Copy events from one project to another.

Service Account must have Recommendations Reader access in the source
project, and Recommendations Editor access in the destination
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
    help='API key')
parser.add_argument(
    '--src_project',
    required=True,
    type=str,
    help='Source cloud project #')
parser.add_argument(
    '--dest_project',
    required=True,
    type=str,
    help='Destination cloud project #')
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


os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = args.service_account

service = build('recommendationengine',
                'v1beta1',
                discoveryServiceUrl=
                'https://recommendationengine.googleapis.com/'
                '$discovery/rest?version=v1beta1&key=' + args.apikey)

next_page = ''
total = 0
while next_page is not None:

  request = service.projects().locations().catalogs().eventStores()\
      .userEvents().list(
          parent='projects/'+ args.src_project +
          '/locations/global/catalogs/default_catalog'+
          '/eventStores/default_event_store',
          filter=filter_string,
          pageSize=5000, pageToken=next_page)

  response = request.execute()

  if 'nextPageToken' in response:
    next_page = response['nextPageToken']
  else:
    next_page = None

  import_body = {}
  import_body['inputConfig'] = {}
  import_body['inputConfig']['userEventInlineSource'] = {}
  import_body['inputConfig']['userEventInlineSource']['userEvents'] = []

  for event in response['userEvents']:
    try:  # Add currencyCode since it's not returned currently (bug #130748472)
      for i in range(len(event['productEventDetail']['productDetails'])):
        event['productEventDetail']['productDetails'][i]['currencyCode'] = 'USD'
    except KeyError:
      pass

    (import_body['inputConfig']['userEventInlineSource']['userEvents']
     .append(event))

  total = total +\
      len(import_body['inputConfig']['userEventInlineSource']['userEvents'])

  # TODO(elarson): Add exponential backoff on the import_request
  # Sometimes import breaks (quota, etc) so we need to recontinue
  #  if (total <= 635000):
  #    continue

  print('Importing 5000')
  import_request = service.projects().locations().catalogs().eventStores()\
      .userEvents().import_(
          parent='projects/'+ args.dest_project +
          '/locations/global/catalogs/default_catalog'+
          '/eventStores/default_event_store',
          body=import_body
          )

  response = import_request.execute()
  if 'done' not in response:
    print(response)

print('Imported ' + str(total) + ' events')
