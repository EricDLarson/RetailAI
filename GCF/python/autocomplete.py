""" Google Cloud Function to return JSON or HTML from autocomplete
This sample uses the Retail API with client libraries

This can be used for doing AJAX/client side calls to get autocomplete results
and render in a div below search box.

Configure the GCF to use a service account which has Retail Viewer Role
"""

import google.auth
import json

from google.cloud import retail
from google.oauth2 import service_account
from google.protobuf.json_format import MessageToDict

PROJECT_NUMBER='<your project #>'

credentials, project = google.auth.default()

# For local testing you may want to do something like this if
# your default credentials don't have Retail/Recommendations Viewer Role
# SERVICE_ACCOUNT_FILE = '<path to local SA key file>'
# credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
# You can also just set an environment variable:
# export GOOGLE_APPLICATION_CREDENTIALS=/path/to/local/SA-key-file

client = retail.CompletionServiceClient(credentials=credentials)

def complete(request):

  if request.args and 'q' in request.args:
    query_string = request.args.get('q')
  else:
    query_string = ''

  request = retail.CompleteQueryRequest(
      catalog='projects/' + PROJECT_NUMBER + '/locations/global/catalogs/default_catalog',
      dataset='cloud-retail',
      query=query_string,
  )

  # Make the request
  response = client.complete_query(request=request)

  # Handle the response
  res = MessageToDict(response._pb)

  result = 'displayAC(' + json.dumps(res) + ')'

  # Set as needed for your CORS policy:
  headers = {
    'Access-Control-Allow-Origin': '*'
  }

  return (result,200,headers)
