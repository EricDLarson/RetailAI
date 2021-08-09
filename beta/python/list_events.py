#!/usr/bin/python3
"""List all Recommendations AI User Events for a given time period.

Returns one json response per line
This is useful for importing into BigQuery or other offline analysis:
https://cloud.google.com/bigquery/docs/loading-data-cloud-storage-json

Can also import directly to BigQuery (create a table with all-events-schema.json)
Using GCS import is usualy faster than inline, 
which only streams up to 5000 events per call
"""

import argparse
import json
from apiclient.discovery import build
from google.oauth2 import service_account
from google.cloud import bigquery
from google.cloud import storage

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
    help='detail-page-view, add-to-cart, purchase-complete, etc')
parser.add_argument(
    '--events_missing_catalog_items',
    required=False,
    action='store_true',
    help='Return only unjoined events')
parser.add_argument(
    '--bq_table',
    required=False,
    type=str,
    help='Stream events to a BigQuery table')
parser.add_argument(
    '--gcs_bucket',
    required=False,
    type=str,
    help='temp bucket for writing event files')
parser.add_argument(
  '-v', '--verbose',
  required=False,
  action='store_true',
  help='Verbose output')

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

if args.bq_table:
  bq = bigquery.Client(credentials=credentials)

if args.gcs_bucket:
  gcs = storage.Client(credentials=credentials)
  gcs_data = ''
  file_num = 1;
  
service = build('recommendationengine',
                'v1beta1',
                discoveryServiceUrl=
                'https://recommendationengine.googleapis.com/'
                '$discovery/rest?version=v1beta1&key=' + args.apikey,
                credentials=credentials
               )

next_page = ''
while next_page is not None:

  if args.verbose:
    print('Getting Recommendations Events')
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
    bq_list = []
    for event in response['userEvents']:
      try:  # Add currencyCode since it's not returned currently (b/130748472)
        for i in range(len(event['productEventDetail']['productDetails'])):
          event['productEventDetail']['productDetails'][i]['currencyCode'] = (
              'USD')
      except KeyError as err:
        pass
      
      if args.bq_table:
        # Remove some attributes when importing into BQ

        if 'eventDetail' in event:
          if 'eventAttributes' in event['eventDetail']:
            if 'categoricalFeatures' in event['eventDetail']['eventAttributes']:
              if 'ecommerce.actionField.affiliation' in event['eventDetail']['eventAttributes']['categoricalFeatures']:
                del(event['eventDetail']['eventAttributes']['categoricalFeatures']['ecommerce.actionField.affiliation'])
            
        if 'productEventDetail' in event:
          if 'productDetails' in event['productEventDetail']:
            for item in event['productEventDetail']['productDetails']:
              if 'itemAttributes' in item:
                del(item['itemAttributes'])
          if 'purchaseTransaction' in event['productEventDetail']:
            if 'costs' in event['productEventDetail']['purchaseTransaction']:
              del(event['productEventDetail']['purchaseTransaction']['costs'])
            if 'taxes' in event['productEventDetail']['purchaseTransaction']:
              del(event['productEventDetail']['purchaseTransaction']['taxes'])
              

        if args.gcs_bucket:
          gcs_data += json.dumps(event) + "\n"
        else:
          bq_list.append(event)
          
      else:
        print(json.dumps(event))

    # Upload to BQ
    if args.bq_table:
      # Use GCS (faster)
      if args.gcs_bucket:
        if (len(gcs_data) > 500000000 or next_page is None):
          if args.verbose:
            print('Writing to GCS')
            print('Data Size: ' + str(len(gcs_data)))
          bucket = gcs.bucket(args.gcs_bucket)
          blob = bucket.blob('events-' + str(file_num) + '.txt')
          gcs_file = blob.upload_from_string(gcs_data)

          if args.verbose:
            print ('Doing BigQuery Import')
          job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
          )
          uri = 'gs://' + args.gcs_bucket + '/' + 'events-' + str(file_num) + '.txt'

          load_job = bq.load_table_from_uri(
            uri,
            args.bq_table,
            location="US",
            job_config=job_config
          )

          gcs_data = ''
          file_num += 1

      # inline import (slow)
      else:
        if args.verbose:
          print ('Writing to BigQuery')
        errors = bq.insert_rows_json(args.bq_table, bq_list)
        if errors:
          print(json.dumps(errors))
          exit()
        else:
          if args.verbose:
            print('Wrote ' + str(len(bq_list)) + ' events to BiqQuery')
        bq_list = []
              
  except KeyError as err:
    print(err)
    pass
