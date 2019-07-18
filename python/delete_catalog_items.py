#!/usr/bin/python3
"""Script to delete items in Recommendations AI catalog.

"""

import argparse
import os
from apiclient.discovery import build
from googleapiclient.errors import HttpError

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

group = parser.add_mutually_exclusive_group(required=True)
group.add_argument(
    '--delete_all_items',
    required=False,
    action='store_true',
    help='Delete ALL items in catalog')
group.add_argument(
    '--items',
    required=False,
    type=str,
    help='item, or list of items to delete.  ex: 12345,12346,12347')

args = parser.parse_args()

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = args.service_account

service = build('recommendationengine',
                'v1beta1',
                discoveryServiceUrl=
                'https://recommendationengine.googleapis.com/'
                '$discovery/rest?version=v1beta1&key=' + args.apikey)

next_page = ''
while next_page is not None:
  if args.delete_all_items:
    request = service.projects().locations().catalogs().catalogItems().list(
        parent='projects/'+ args.project +
        '/locations/global/catalogs/default_catalog',
        pageSize=1000, pageToken=next_page)
    response = request.execute()

    if 'nextPageToken' in response:
      next_page = response['nextPageToken']
    else:
      next_page = None
  else:  # Create our own 'response' with the item ids
    next_page = None
    response = {
        'catalogItems': []
    }
    for item in args.items.split(','):
      i = {'id': item}
      response['catalogItems'].append(i)

  for item in response['catalogItems']:
    print('Deleting item id ' + item['id'])
    request = service.projects().locations().catalogs().catalogItems().delete(
        name='projects/' + args.project +
        '/locations/global/catalogs/default_catalog/catalogItems/' + item['id'])
    try:
      response = request.execute()
    except HttpError as err:
      print(err)
