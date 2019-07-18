#!/bin/bash

# Import events from GCS bucket, as specified in event_import.json

export GOOGLE_APPLICATION_CREDENTIALS=<yourkeyfile>
export PROJECT=<yourprojectnumber>

curl -X POST \
  -H "Content-Type: application/json; charset=utf-8" -d @/tmp/event_import.json \
  -H "Authorization: Bearer "$(gcloud auth application-default print-access-token)"" \
  "https://recommendationengine.googleapis.com/v1beta1/projects/$PROJECT/locations/global/catalogs/default_catalog/eventStores/default_event_store/userEvents:import"
