#!/bin/bash

# Delete events using the purge method:
# https://cloud.google.com/recommendations-ai/docs/reference/rest/v1beta1/projects.locations.catalogs.eventStores.userEvents/purge
# The filter field specifies a time range (eventTime) and/or eventType
# Note the encoding for the filter parameter, and times are in "zulu" format.  In this case we've encoded:
# filter=eventTime > "2000-04-23T18:25:43.511Z" eventTime < "2001-04-23T18:30:43.511Z"

export GOOGLE_APPLICATION_CREDENTIALS=<yourkeyfile>
export PROJECT=<yourprojectnumber>

curl -H "Authorization: Bearer "$(gcloud auth application-default print-access-token)"" \
     \"https://recommendationengine.googleapis.com/v1beta1/projects/$PROJECT/locations/global/catalogs/default_catalog/eventStores/default_event_store/userEvents:purge?filter=eventTime%20%3E%20%222000-04-23T18%3A25%3A43.511Z%22%20eventTime%20%3C%20%222001-04-23T18%3A30%3A43.511Z%22\"
