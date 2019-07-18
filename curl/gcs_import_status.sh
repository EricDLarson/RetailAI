#!/bin/bash

# Display status of GCS catalog or event import job
# Will usually show "done" - errors written to errorsConfig bucket

export GOOGLE_APPLICATION_CREDENTIALS=<yourkeyfile>
export PROJECT=<yourprojectnumber>

curl -H "Authorization: Bearer "$(gcloud auth application-default print-access-token)"" \
  "https://recommendationengine.googleapis.com/v1beta1/projects/$PROJECT/locations/global/catalogs/default_catalog/operations/$1"
