#!/usr/bin/python3
"""Export Catalog from BQ to json import txt file.

Currently just outputs to stdout, so pipe to a file.
Import files should be <500MB, so may require splitting the resulting file.
"""

import argparse
import json
import os
import re
from google.cloud import bigquery

parser = argparse.ArgumentParser()
parser.add_argument(
    '--service_account',
    required=True,
    type=str,
    help='Path to service account .json key file')
parser.add_argument(
    '--bqtable',
    required=True,
    type=str,
    help='Table Name for MC Data')

args = parser.parse_args()

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = args.service_account

client = bigquery.Client()
query = ('SELECT * FROM `' + args.bqtable + '` '
         'WHERE _PARTITIONTIME IN ('
         'SELECT MAX(_PARTITIONTIME) '
         'FROM `' + args.bqtable + '`)')
query_job = client.query(query)

for row in query_job:
  # Build a CatalogItem:
  # https://cloud.google.com/recommendations-ai/docs/reference/rest/v1beta1/projects.locations.catalogs.catalogItems#CatalogItem

  try:  # This will skip any records with missing data
    rec_json = {}
    rec_json['id'] = row.get('offer_id')
    rec_json['categoryHierarchies'] = {
        'categories': re.split(' > |,', row.get('product_type'))
    }
    rec_json['title'] = row.get('title')
    rec_json['description'] = row.get('description')
    rec_json['languageCode'] = row.get('content_language')
    rec_json['productMetadata'] = ({
        'currencyCode': row.get('price')['currency'],
        'canonicalProductUri': row.get('link'),
        'exactPrice': {
            'displayPrice': row.get('price')['value']
        },
        'availableQuantity': '1',
    })

    # Customize for extra attributes as necessary
    if (row.get('mpm') or row.get('gtin')):
      rec_json['itemAttributes'] = ({
          'categoricalFeatures': {
          }
      })

      if row.get('mpm'):
        rec_json['itemAttributes']['categoricalFeatures']['mpm'] = ({
            'value': [row.get('mpm')]
        })

      if row.get('gtin'):
        rec_json['itemAttributes']['categoricalFeatures']['gtin'] = {
            'value': [row.get('gtin')]
        }

    print(json.dumps(rec_json))
  except KeyError:
    pass
