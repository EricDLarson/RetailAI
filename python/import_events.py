#!/usr/bin/python3
"""Read one JSON struct per line from file and import to Recommendations AI.

This shouldn't be used for very large imports, use gcsSource instead:
https://cloud.google.com/recommendations-ai/docs/reference/rest/v1beta1/InputConfig#GcsSource
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
parser.add_argument(
    '--infile',
    required=False,
    type=str,
    help='Input File, use stdinn if omitted')

args = parser.parse_args()

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = args.service_account

service = build('recommendationengine',
                'v1beta1',
                discoveryServiceUrl=
                'https://recommendationengine.googleapis.com/'
                '$discovery/rest?version=v1beta1&key=' + args.apikey)


def main():
  count = 0
  if args.infile:
    infile = open(args.infile, 'r')
  else:
    infile = sys.stdin

  for line in infile:
    data = json.loads(line)
    count = count + 1

    if count == 1:
      import_body = {}
      import_body['inputConfig'] = {}
      import_body['inputConfig']['userEventInlineSource'] = {}
      import_body['inputConfig']['userEventInlineSource']['userEvents'] = []

    (import_body['inputConfig']['userEventInlineSource']['userEvents']
     .append(data))

    if count == 5000:
      import_event(import_body)
      count = 0

  if count > 0:
    import_event(import_body)


def import_event(json_body):
  """Upload up to 5000 events using userEvents.import()."""

  event_count = \
      len(json_body['inputConfig']['userEventInlineSource']['userEvents'])

  print('Importing ' + str(event_count))

  import_request = service.projects().locations().catalogs().eventStores()\
    .userEvents().import_(
        parent='projects/'+ args.project +
        '/locations/global/catalogs/default_catalog'+
        '/eventStores/default_event_store',
        body=json_body
        )

  response = import_request.execute()
  if 'done' not in response:
    print(response)

if __name__ == '__main__':
  main()
