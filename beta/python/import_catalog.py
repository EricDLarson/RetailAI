#!/usr/bin/python3
"""Import catalog from file to Recommendations AI.

Currently supports Merchant Center file format (TSV, tab-delimited only):
https://support.google.com/merchants/answer/160567?hl=en
Uses only the following fields from the MC TSV file:
id, link, title, description, product_type, availability, price
"""

import argparse
import csv
import os
import re
import sys
from apiclient.discovery import build

LANGUAGE_CODE = 'en'

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
  if args.infile:
    infile = open(args.infile, 'r')
  else:
    infile = sys.stdin

  count = 0
  reader = csv.DictReader(infile, dialect='excel-tab')
  for row in reader:
    if count == 0:
      import_body = {
          'inputConfig': {
              'catalogInlineSource': {
                  'catalogItems': []
              }
          }
      }

    item = {
        'id': row['id'],
        'languageCode': LANGUAGE_CODE,
        'title': row['title'],
        'description': row['description'],
        'categoryHierarchies': {
            # May need to tweak this based on your categories:
            'categories': re.split(' > |,', row['product_type'])
        },
        'productMetadata': {
            'currencyCode': 'USD',
            'canonicalProductUri': row['link'],
            'exactPrice': {
                'originalPrice': row['price']
            },
            'images': []
        },
        'itemAttributes': {
            'categoricalFeatures': {

            }
        },
        'tags': []
    }

    if row['availability'] == 'in stock':
      item['productMetadata']['stockState'] = 'IN_STOCK'
    else:
      item['productMetadata']['stockState'] = 'OUT_OF_STOCK'

    # Optional Fields
    if row['weight']:
      item['itemAttributes']['categoricalFeatures']['weight'] = {
          'value': [row['weight']]
      }
    if row['brand']:
      item['itemAttributes']['categoricalFeatures']['brand'] = {
          'value': [row['brand']]
      }
    if row['condition']:
      item['itemAttributes']['categoricalFeatures']['condition'] = {
          'value': [row['condition']]
      }

    (import_body['inputConfig']['catalogInlineSource']['catalogItems']
     .append(item))

    count = count + 1

    if count == 5000:
      import_catalog(import_body)
      count = 0
      import_body = {}

  import_catalog(import_body)


def import_catalog(json_body):
  """Upload up to 5000 events using catalogItems.import()."""

  event_count = \
      len(json_body['inputConfig']['catalogInlineSource']['catalogItems'])

  print('Importing ' + str(event_count))

  import_request = service.projects().locations().catalogs().catalogItems()\
    .import_(
        parent='projects/{}/locations/global/catalogs/default_catalog'
        .format(args.project),
        body=json_body
        )

  response = import_request.execute()
  if 'done' not in response:
    print(response)


if __name__ == '__main__':
  main()
