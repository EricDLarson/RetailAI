#!/usr/bin/python3
"""Script to list items in Recommendations AI catalog.

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
    '--project',
    required=True,
    type=str,
    help='cloud project #')
parser.add_argument(
    '--simple',
    required=False,
    action='store_true',
    help='Display itemId & Title Only')


args = parser.parse_args()

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = args.service_account

service = build('recommendationengine',
                'v1beta1',
                discoveryServiceUrl=
                'https://recommendationengine.googleapis.com/'
                '$discovery/rest?version=v1beta1&key=' + args.apikey)

next_page = ''
while next_page is not None:
  request = service.projects().locations().catalogs().catalogItems().list(
      parent='projects/'+ args.project +
      '/locations/global/catalogs/default_catalog',
      pageSize=1000, pageToken=next_page)
  response = request.execute()

  if 'nextPageToken' in response:
    next_page = response['nextPageToken']
  else:
    next_page = None

  for item in response['catalogItems']:
    if args.simple:
      print('{:s}:{:s}'.format(item['id'], item['title']))
    else:
      print(item)
