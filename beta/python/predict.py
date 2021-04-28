#!/usr/bin/python3
"""Call prediction API, return recommendations.

There are a lot of options for passing in different events to predict.
This is just a very basic sample that can easily be extended.
"""

import argparse
import pprint
from apiclient.discovery import build

parser = argparse.ArgumentParser()
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
    '--placementid',
    required=True,
    type=str,
    help='placement id, ie: product_detail')
parser.add_argument(
    '--items',
    required=False,
    type=str,
    help='item, or list of items for prediction.  ex: 12345,12346,12347')
parser.add_argument(
    '--visitorid',
    type=str,
    default='visitor1')
parser.add_argument(
    '--userid',
    type=str,
    default='user1')

args = parser.parse_args()

service = build('recommendationengine',
                'v1beta1',
                discoveryServiceUrl=
                'https://recommendationengine.googleapis.com/'
                '$discovery/rest?version=v1beta1',
                developerKey=args.apikey)

json_body = {
    'pageSize': 5,
    'dryRun': False,
    'userEvent': {
        'userInfo': {
            'visitorId': args.visitorid,
            'userId': args.userid,
            'ipAddress': '0.0.0.0',
            'userAgent': 'Test'
        },
        'eventDetail': {
            # 'experimentIds': 'experiment-group'
        }
    }
}


if args.items is not None:
  json_body['userEvent']['eventType'] = 'detail-page-view'
  json_body['userEvent']['productEventDetail'] = {
      'productDetails': [],
  }
  for item in args.items.split(','):
    (json_body['userEvent']['productEventDetail']['productDetails']
     .append({'id': item}))
else:
  json_body['userEvent']['eventType'] = 'home-page-view'

pprint.pprint(json_body)

request = service.projects().locations().catalogs().eventStores()\
      .placements().predict(
          name='projects/'+ args.project +
          '/locations/global/catalogs/default_catalog'+
          '/eventStores/default_event_store/placements/'+args.placementid,
          body=json_body)  # body takes a python dict, converts to json

response = request.execute()
pprint.pprint(response)
