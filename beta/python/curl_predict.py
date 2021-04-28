#!/usr/bin/python3

# This sample constructs and executes a simple curl command to call the
# predict API,

import argparse
import os
import json

APIKEY='<your registered API key>'
PROJECT='<your project number>'
PLACEMENT='<your placement id>'

parser = argparse.ArgumentParser()
parser.add_argument('itemids',
                    help='comma-seperated list of item ids')

args = parser.parse_args()

data = {
    'dryRun': False,
    'pageSize': 4,
    'params': {
        'returnCatalogItem': True,
        'returnItemScore': True
    },
    'userEvent': {
        'eventType': 'detail-page-view',
        'userInfo': {
            'visitorId': 'visitor1',
            'userId': 'user1',
            'ipAddress': '0.0.0.0',
            'userAgent': 'Mozilla/5.0 (Windows NT 6.1)'
        },
      'productEventDetail': {
        'productDetails': [
        ]
      }
    }
}

for id in args.itemids.split(','):
  data['userEvent']['productEventDetail']['productDetails'].append(
    {'id': str(id)}
  )


CMD='curl -X POST -H "Content-Type: application/json; charset=utf-8" ' + \
'--data  \'' + json.dumps(data) + \
'\' https://recommendationengine.googleapis.com/v1beta1/projects/' + \
PROJECT + \
'/locations/global/catalogs/default_catalog/eventStores' + \
'/default_event_store/placements/' + \
PLACEMENT + ':predict?key=' + APIKEY

print(CMD)
os.system(CMD)

