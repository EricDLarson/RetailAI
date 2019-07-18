#!/bin/bash

# Add a catalog item from testitem.json file

export GOOGLE_APPLICATION_CREDENTIALS=<yourkeyfile>
export PROJECT=<yourprojectnumber>

curl -X POST \
  -H "Authorization: Bearer $(gcloud auth application-default print-access-token)" \
  -H "Content-Type: application/json; charset=utf-8" \
  --data @./testitem.json \
  "https://recommendationengine.googleapis.com/v1beta1/projects/$PROJECT/locations/global/catalogs/default_catalog/catalogItems"
