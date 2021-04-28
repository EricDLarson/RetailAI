#!/bin/bash

# Register a key for use with predict API
# usage: ./register_key.sh <key>

export GOOGLE_APPLICATION_CREDENTIALS=<yourkeyfile>
export PROJECTID=<yourprojectnumber>

curl -X POST \
     -H "Authorization: Bearer $(gcloud auth application-default print-access-token)" \
     -H "Content-Type: application/json; charset=utf-8" \
     --data '{ 
           "predictionApiKeyRegistration": { 
                "apiKey": "'"$1"'"
            } 
        }'\
        "https://recommendationengine.googleapis.com/v1beta1/projects/$PROJECTID/locations/global/catalogs/default_catalog/eventStores/default_event_store/predictionApiKeyRegistrations"
