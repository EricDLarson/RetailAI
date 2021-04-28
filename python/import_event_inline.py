#!/usr/bin/python3

""" Inline import user events using Retail API

This example shows how to construct a timestamp (using current time)

"""

import datetime

from google.cloud import retail
from google.oauth2 import service_account
from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf.wrappers_pb2 import Int32Value

SERVICE_ACCOUNT_FILE = "<path to service account json file>"
PROJECT_NUM = "<project # or id>"

SCOPES = ['https://www.googleapis.com/auth/cloud-platform']
credentials = service_account.Credentials.from_service_account_file(
  SERVICE_ACCOUNT_FILE, scopes=SCOPES)

client = retail.UserEventServiceClient(credentials=credentials)

timestamp = Timestamp()
timestamp.FromDatetime(dt=datetime.datetime.now())

quantity = Int32Value(value=1)

user_events = {
  "user_events": [
    {
      "event_type": "home-page-view",
      "event_time": timestamp,
      "visitor_id": "visitor-1",
      "user_info": {
        "user_id": "user12345"
      }
    },
    {
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
    },
    {
      "event_type": "add-to-cart",
      "event_time": timestamp,
      "visitor_id": "visitor-1",
      "user_info": {
        "user_id": "user12345"
      },
      "product_details": [{
        "product": {
          "id": "12345"
        },
        "quantity": quantity
      }]
    },
    {
      "event_type": "purchase-complete",
      "event_time": timestamp,
      "visitor_id": "visitor-1",
      "user_info": {
        "user_id": "user12345"
      },
      "product_details": [{
        "product": {
          "id": "12345"
        },
        "quantity": quantity
      }],
      "purchase_transaction": {
        "id": "567",
        "revenue": 19.95,
        "currency_code": "USD"
      }
    }
  ]
}

request = {
  "parent":
    'projects/' + PROJECT_NUM + '/locations/global/catalogs/default_catalog',
  "input_config": {"user_event_inline_source": user_events}
}

response = client.import_user_events(request)
