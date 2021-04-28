#!/usr/bin/python3

""" Sample predict call showing how to pass event

Customize with placement, event type as needed

"""

import datetime

from google.cloud import retail
from google.oauth2 import service_account
from google.protobuf.timestamp_pb2 import Timestamp

SERVICE_ACCOUNT_FILE = "<path to service account json file>"
PROJECT_NUM = "<project # or id>"

SCOPES = ['https://www.googleapis.com/auth/cloud-platform']
credentials = service_account.Credentials.from_service_account_file(
  SERVICE_ACCOUNT_FILE, scopes=SCOPES)

client = retail.PredictionServiceClient(credentials=credentials)

timestamp = Timestamp()
timestamp.FromDatetime(dt=datetime.datetime.now())

user_event = {
  "event_type": "detail-page-view",
  "event_time": timestamp,
  "visitor_id": "visitor-1",
  "user_info": {
    "user_id": "user12345"
  },
  "product_details": [{
    "product": {
      "id": "12345"
    }
  }]
}

request = {
  "placement":
    'projects/' + PROJECT_NUM +
    '/locations/global/catalogs/default_catalog/placements/home_page',
  
  "user_event": user_event,

  "filter": "filterOutOfStockItems",

  "params": {
    "returnProduct": True,
    "returnScore": True
  }
}

response = client.predict(request)

print(response)
