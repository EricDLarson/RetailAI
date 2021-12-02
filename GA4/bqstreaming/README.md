# GA4 BigQuery Streaming Ingestion Tool

## Overview

You can export all of your raw events from [Google Analytics 4 properties to BigQuery](https://support.google.com/analytics/answer/9823238#step3&zippy=%2Cin-this-article)
, and ingest the data into the retail API using the [CollectUserEvent method](https://cloud.google.com/retail/docs/reference/rest/v2/projects.locations.catalogs.userEvents/collect).
This is a Cloud Function example that collects GA4 schema data stored in
BigQuery tables and ingests the data into the retail API.
The required parameters needed by this tool will be passed through the
environment variables and request bodies.
Please refer to the comments of `userEventIngester` and `envVariables` in
"ingestuserevents.go" file to learn the parameters and variables.

## Before you begin

Contact cips-dh@google.com to get allowlisted to use the data harmonization
features.

## Create a Cloud Function

You may follow the toturial
[Your First Function: Go](https://cloud.google.com/functions/docs/first-go) to
learn how to create a Cloud Function. We list the core commands needed below:

1.  Enable services:

    ```
    gcloud services enable cloudbuild.googleapis.com
    gcloud services enable cloudfunctions.googleapis.com
    ```

1.  Grant permissions:

    ```
    BQProjectID=<ID-of-project-that-has-GA4-BQ-tables>
    CFProjectID=<ID-of-project-that-runs-cloud-function>
    gcloud projects add-iam-policy-binding ${BQProjectID} \
        --member=serviceAccount:${CFProjectID}@appspot.gserviceaccount.com --role=roles/bigquery.jobUser
    gcloud projects add-iam-policy-binding ${BQProjectID} \
        --member=serviceAccount:${CFProjectID}@appspot.gserviceaccount.com --role=roles/bigquery.dataViewer
    ```

1.  Create an API key to access the retail API

    You may follow the instructions in
    [Recommendations AI Before you begin](https://cloud.google.com/retail/recommendations-ai/docs/setting-up#create-key)
    to create the API key.

1.  Create a directory on your local system for the function code:

    ```
    mkdir ~/ingestuserevents
    cd ~/ingestuserevents
    ```

1.  Copy the go files to the directory "~/ingestuserevents".

1.  Specify the dependencies:

    ```
    go mod init ingestuserevents
    go mod tidy
    ```

1.  Deploy the function

    ```
    gcloud functions deploy IngestUserEvents \
    --runtime go116 --trigger-http --allow-unauthenticated \
    --set-env-vars=\
    MetadataProjectID=${CFProjectID},\
    RetailProjectNumber=<the-number-of-project-that-enables-the-retail-API>,\
    APIKey=<API-key-that-can-access-the-retail-API>,\
    TaskName=<any-arbitrary-string>
    ```

1.  Test the function

    You should pass some parameters like below in the request body:

    ```
    {
        "BQProjectID":"<ID-of-project-that-has-GA4-BQ-tables>",
        "BQDatasetID":"<ID-of-dataset-that-has-GA4-BQ-tables>",
        "DurationInSeconds":70
    }
    ```

## Create a scheduled job

We want to use the Cloud Scheduler to trigger the Cloud Function:

```
gcloud scheduler jobs create http ingest-user-events \
  --description "Ingest user events hourly" \
  --schedule "*/1 * * * *" \
  --time-zone "Canada/Toronto" \
  --uri "https://${REGION}-${PROJECT_ID}.cloudfunctions.net/IngestUserEvents" \
  --http-method GET \
  --message-body '{"BQProjectID":"<foo>","BQDatasetID":"<bar>","DurationInSeconds":70}'
```
