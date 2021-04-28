#!/usr/bin/python3
""" Inline import catalog items using Retail API

"""

from google.cloud import retail
from google.oauth2 import service_account

SERVICE_ACCOUNT_FILE = "<path to service account json file>"
PROJECT_NUM = "<project # or id>"

SCOPES = ['https://www.googleapis.com/auth/cloud-platform']
credentials = service_account.Credentials.from_service_account_file(
  SERVICE_ACCOUNT_FILE, scopes=SCOPES)

client = retail.ProductServiceClient(credentials=credentials)

products = {
    "products": [
      {
        "id": "123",
        "title": "Steamed Hams",
        "description": "Bulk Lot of Steamed Hams",
        "categories": ["Food","Steamed & Canned"],
        "price_info": {
          "price": 149.95,
          "currency_code": "USD"
        }
      },
      {
        "id": "456",
        "title": "Canned Yams",
        "description": "Bulk Lot of Canned Yams",
        "categories": ["Food","Steamed & Canned"],
        "price_info": {
          "price": 89.95,
          "currency_code": "USD"
        }
      }
    ]
}
  
request = {
  "parent": 'projects/' + PROJECT_NUM + '/locations/global/catalogs/default_catalog/branches/0',
  "input_config": {"product_inline_source": products}
}

response = client.import_products(request)

