#!/bin/bash

# usage: ./get_catalog_item.sh <item id>

export GOOGLE_APPLICATION_CREDENTIALS=<yourkeyfile>
export PROJECT=<yourprojectnumber>

curl -H "Authorization: Bearer $(gcloud auth application-default print-access-token)"  \
  -H "Content-Type: application/json; charset=utf-8" \
  "https://recommendationengine.googleapis.com/v1beta1/projects/$PROJECT/locations/global/catalogs/default_catalog/catalogItems/$1"
