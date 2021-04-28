#!/bin/bash

# Get list of registered predict keys

export GOOGLE_APPLICATION_CREDENTIALS=<yourkeyfile>
export PROJECT=<yourprojectnumber>

curl -X GET \
     -H "Authorization: Bearer $(gcloud auth application-default print-access-token)" \
     -H "Content-Type: application/json; charset=utf-8" \
     "https://recommendationengine.googleapis.com/v1beta1/projects/$PROJECTID/locations/global/catalogs/default_catalog/eventStores/default_event_store/predictionApiKeyRegistrations"
