#!/bin/bash

# Delete an item from the catalog
# Usage: ./delete_item.sh itemid

export GOOGLE_APPLICATION_CREDENTIALS=<yourkeyfile>
export PROJECT=<yourprojectnumber>

curl -X DELETE \
  -H "Authorization: Bearer $(gcloud auth application-default print-access-token)" \
  "https://recommendationengine.googleapis.com/v1beta1/projects/$PROJECT/locations/global/catalogs/default_catalog/catalogItems/$1"
