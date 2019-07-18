"""Cloud function for returning JSON via AJAX request (JSONP).

Simply deploy this as a cloud function with your correct API KEY and project
"""

import json
import requests

API_KEY = '<yourpredictapikey>'
PROJECT_NUMBER = '<yourprojectnumber>'


def recommend(request):
  """Main function to be called.

  Args:
    request: Flask HTTP request.
  Returns:
    A string (JSONP function in this case)
  """

  if request.args and 'visitorid' in request.args:
    visitorid = request.args.get('visitorid')
  else:
    visitorid = ''

  if request.args and 'productid' in request.args:
    productid = request.args.get('productid')
  else:
    productid = ''

  if request.args and 'num' in request.args:
    page_size = request.args.get('num')
  else:
    page_size = 4

  payload = {
      'filter': 'filterOutOfStockItems tag="safe"',
      'pageSize': page_size,
      'params': {
          'returnCatalogItem': True
      },
      'userEvent': {
          'eventType': 'detail-page-view',
          'userInfo': {
              'visitorId': visitorid,
          },
          'productEventDetail': {
              'productDetails': [{
                  'id': productid,
                  'currencyCode': 'USD'
              }]
          }
      }
  }

  r = requests.post(('https://recommendationengine.googleapis.com/v1beta1/'
                     'projects/' + PROJECT_NUMBER + '/locations/global/'
                     'catalogs/default_catalog/'
                     'eventStores/default_event_store/'
                     'placements/product_detail:predict?key=' + API_KEY),
                    data=json.dumps(payload))

  # Return JSONP result
  result = 'displayRecs(' + r.text + ')'

  return result
