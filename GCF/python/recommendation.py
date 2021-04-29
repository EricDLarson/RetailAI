""" Google Cloud Function to return JSON or HTML from predict response

This sample uses the Retail API with client libraries

This can be used for doing AJAX/client side calls to get prediction results
and render in a div.

Configure the GCF to use a service account which has Retail Editor Role

"""

import google.auth
import json

from google.cloud import retail
from google.oauth2 import service_account

PROJECT_NUMBER='718209125704'

credentials, project = google.auth.default(
    scopes=[
      'https://www.googleapis.com/auth/cloud-platform'
    ]
)

client = retail.PredictionServiceClient(credentials=credentials)

def recommend(request):

  if request.args and 'visitorid' in request.args:
    visitorid = request.args.get('visitorid')
  else:
    visitorid = ""

  if request.args and 'productid' in request.args:
    productid = request.args.get('productid')
  else:
    productid = ""

  if request.args and 'num' in request.args:
    pageSize = request.args.get('num')
  else:
    pageSize = 4

  user_event = {
    'event_type': 'detail-page-view',
    'visitor_id': visitorid,
    'product_details': [{
      'product': {
        'id': productid,
      }
    }]
  }

  # Set as necessary for your requirements & placement id:
  predict_request = {
    "placement":
      'projects/' + PROJECT_NUMBER +
      '/locations/global/catalogs/default_catalog/placements/product_detail',

    "user_event": user_event,

    "page_size": pageSize,

    "filter": 'filterOutOfStockItems tag="safe"',

    "params": {
      "returnProduct": True,
      "returnScore": True
    }
  }

  response = client.predict(predict_request)

  # Configure as necessary - here we just return a few fields
  # that we need for rendering the results
  items = []
  for rec in response.results:
    product = rec.metadata.get('product')
    images = product.get('images')

    item = {
      "id": rec.id,
      "title": product.get('title'),
      "uri": product.get('uri'),
      "img": images[0]['uri']
    }

    items.append(item)

  # option to return full div or JSON
  if request.args and 'html' in request.args:
    result = '<div>'

    for item in items:
      result =(result + '<img src="' + item['uri'] + '">')

    result = result + '</div>'

  else:
    result = 'displayRecs(' + json.dumps(items) + ')'

  return (result)
