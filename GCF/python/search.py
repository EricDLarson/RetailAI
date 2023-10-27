""" Google Cloud Function to return JSON or HTML from search response
This sample uses the Retail API with client libraries

This can be used for doing AJAX/client side calls to get search results
and render in a div.

Configure the GCF to use a service account which has Retail Editor Role
"""

import google.auth
import json

from google.cloud import retail
from google.oauth2 import service_account
from google.protobuf.json_format import MessageToDict

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

client = retail.SearchServiceClient(credentials=credentials)

def search(request):

  if request.args and 'visitorid' in request.args:
    visitorid = request.args.get('visitorid')
  else:
    visitorid = ''

  if request.args and 'query' in request.args:
    query = request.args.get('query')
  else:
    query = ''

  if request.args and 'placement' in request.args:
    placement = request.args.get('placement')
  else:
    placement = 'default_search'

  body = {
    'query': query,
    'visitor_id': visitorid
  }

  search_request = {
    'placement':
      'projects/' + PROJECT_NUMBER +
      '/locations/global/catalogs/default_catalog/placements/' + placement,
    'query': query,
    'visitor_id': visitorid
  }

  response = client.search(search_request)

  res = MessageToDict(response._pb)

  result = 'displaySearch(' + json.dumps(res) + ')'

  # Set as needed for your CORS policy:
  headers = {
    'Access-Control-Allow-Origin': '*'
  }

  return (result,200,headers)
