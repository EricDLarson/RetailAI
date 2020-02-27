#!/bin/bash

# Delete events using the purge method:
# https://cloud.google.com/recommendations-ai/docs/reference/rest/v1beta1/projects.locations.catalogs.eventStores.userEvents/purge
# The filter field specifies a time range (eventTime) and/or eventType
# Note the encoding for the filter parameter, and times are in "zulu" format.  In this case we've encoded:
# filter=eventTime > "2000-04-23T18:25:43.511Z" eventTime < "2001-04-23T18:30:43.511Z"
# force:true will cause an actual delete, force:false (the default) will return only return a list of events that match

export GOOGLE_APPLICATION_CREDENTIALS=<yourkeyfile>
export PROJECT_NUM=<yourprojectnumber>

curl -X POST -H "Authorization: Bearer "$(gcloud auth application-default print-access-token)"" \
      -H "Content-Type: application/json; charset=utf-8" \
     --data '{
              "filter":"eventTime > \"2019-12-23T18:25:43.511Z\" eventTime < \"2019-12-23T18:30:43.511Z\"",
              "force":"true"
    }' \
    "https://recommendationengine.googleapis.com/v1beta1/projects/$PROJECT_NUM/locations/global/catalogs/default_catalog/eventStores/default_event_store/userEvents:purge"
