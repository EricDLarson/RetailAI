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

PROJECT_NUMBER='<your project #>'

credentials, project = google.auth.default(
    scopes=[
      'https://www.googleapis.com/auth/cloud-platform'
    ]
)

# For local testing you may want to do something like this if
# your default credentials don't have Retail/Recommendations Viewer Role
# SERVICE_ACCOUNT_FILE = '<path to local SA key file>'
# credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
# You can also just set an environment variable:
# export GOOGLE_APPLICATION_CREDENTIALS=/path/to/local/SA-key-file

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

  if request.args and 'placement' in request.args:
    placement = request.args.get('placement')
  else:
    placement = 'product_detail'

  user_event = {
    'event_type': 'detail-page-view',
    'visitor_id': visitorid,
    'product_details': [{
      'product': {
        'id': productid,
      }
    }]
  }

  predict_request = {
    "placement":
      'projects/' + PROJECT_NUMBER +
      '/locations/global/catalogs/default_catalog/placements/' + placement,

    "user_event": user_event,

    "page_size": pageSize,

    "filter": 'filterOutOfStockItems',

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

    # Customize as needed:
    item = {
      "id": rec.id,
      "title": product.get('title'),
      "uri": product.get('uri'),
      "img": images[1]['uri']
    }

    items.append(item)

  # option to return full div or JSON
  if request.args and 'html' in request.args:
    result = '<div>'

    for item in items:
      result = (result + '<a href="' + item['uri'] + '">' +
        '<img src="' + item['img'] + '"></a>')

    result = result + '</div>'

  else:
    result = 'displayRecs(' + json.dumps(items) + ')'

  # Set as needed for your CORS policy:
  headers = {
    'Access-Control-Allow-Origin': '*'
  }

  return (result,200,headers)
