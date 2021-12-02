// Copyright 2021 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     https://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// Package ingestuserevents contains an HTTP Cloud Function.
package ingestuserevents

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"net/url"
	"os"
	"strconv"
	"strings"
	"time"

	"cloud.google.com/go/bigquery"
	"cloud.google.com/go/logging"
	"google.golang.org/api/iterator"
)

// userEventIngester is a tool to ingest user events.
// The cloud function's request body should includes the following public
// fields.
type userEventIngester struct {
	// ID of the project that the GA4 BigQuery belongs to. (required)
	BQProjectID string `json:"BQProjectID"`
	// ID of the dataset that the GA4 Dataset belongs to. (required)
	BQDatasetID string `json:"BQDatasetID"`
	// A duration in seconds that specifies how long ago the collection should
	// start from comparing to now. It should be a little bit larger than the
	// duration of the Cloud Scheduler that triggers the Cloud Function.
	// For example, if the Cloud Scheduler runs every minutes, its value could
	// be between 65 and 75. (required)
	DurationInSeconds int `json:"DurationInSeconds"`
	// Optional parameters
	// Used for debugging purpose only. This time will overwrite the current time.
	// Example, 20210724070849
	DebugCollectTime string `json:"DebugCollectTime"`
	// request body parameters end.

	// Other intermediate variables.
	writer         io.Writer
	queryParameter queryParameter
}

func (ingester *userEventIngester) debugMode() bool {
	return len(ingester.DebugCollectTime) > 0
}

func (ingester *userEventIngester) valid() error {
	if len(ingester.BQProjectID) == 0 {
		return fmt.Errorf("Argument BQProjectID is not specified")
	}
	if len(ingester.BQDatasetID) == 0 {
		return fmt.Errorf("Argument BQDatasetID is not specified")
	}
	if ingester.DurationInSeconds == 0 {
		return fmt.Errorf("Argument DurationInSeconds is not specified")
	}
	if ingester.DurationInSeconds > int(time.Hour.Seconds()*48) {
		return fmt.Errorf(
			"DurationInSeconds must be a number of seconds smaller than 2 days")
	}
	return nil
}

// ingestResults prints results from a query to the Stack Overflow public dataset.
func (ingester *userEventIngester) ingestResults(ctx context.Context, iter *bigquery.RowIterator) (total int, success int, err error) {
	if err != nil {
		return 0, 0, fmt.Errorf("failed to create retail user event client: %v", err)
	}
	totalNumber := 0
	successNumber := 0
	var ingestErrors []error
	for {
		var row GA4BQRow
		// var row []bigquery.Value
		err := iter.Next(&row)
		if err == iterator.Done {
			break
		}
		if err != nil {
			ingestErrors = append(
				ingestErrors, fmt.Errorf("error iterating through results: %v", err))
			break
		}
		totalNumber++

		b, err := json.Marshal(row)
		if err != nil {
			ingestErrors = append(
				ingestErrors, fmt.Errorf("failed to marshal row: %v", err))
			continue
		}
		err = ingestRetailUserEventRawText(
			ctx, ingester.writer,
			environmentVariables.RetailProjectNumber,
			environmentVariables.APIKey,
			string(b), "ga4_bq")
		if err != nil {
			ingestErrors = append(
				ingestErrors, fmt.Errorf("failed to ingest: %v", err))
			continue
		}
		successNumber++
	}
	if len(ingestErrors) != 0 {
		return totalNumber, successNumber, fmt.Errorf("failed to ingest: %v", ingestErrors)
	}
	return totalNumber, successNumber, nil
}

// envVariables stores all the arguments passed through environment variables.
// All the public variables should be specified in the environment variables.
type envVariables struct {
	// Specified by environment variable MetadataProjectID.
	// ID of a project that the Cloud Function print logs to. You
	// may use the ID of the project that is running the Cloud Functions.
	MetadataProjectID string
	// Specified by environment variable RetailProjectNumber.
	// Number of a project that enables the retail API.
	RetailProjectNumber int64
	// Specified by environment variable APIKey.
	// Key of a service account that has access to the retail API.
	APIKey string
	// Specified by environment variable TaskName.
	// Name of the task. It is an arbitrary string to distinguish between multiple
	// Cloud Functions.
	// It affects the name of the GCS object contains the metadata and the logs.
	TaskName string
}

func (ev *envVariables) validate() error {
	if len(ev.MetadataProjectID) == 0 {
		return fmt.Errorf("Environment variable MetadataProjectID is not specified")
	}
	if ev.RetailProjectNumber == 0 {
		return fmt.Errorf("Environment variable RetailProjectNumber is not specified")
	}
	if len(ev.APIKey) == 0 {
		return fmt.Errorf("Environment variable APIKey is not specified")
	}
	if len(ev.TaskName) == 0 {
		return fmt.Errorf("Environment TaskName is not specified")
	}
	return nil
}

var environmentVariables = envVariables{
	MetadataProjectID: os.Getenv("MetadataProjectID"),
	APIKey:            os.Getenv("APIKey"),
	TaskName:          os.Getenv("TaskName")}

func init() {
	retailProjectNumber := os.Getenv("RetailProjectNumber")
	var err error
	environmentVariables.RetailProjectNumber, err = strconv.ParseInt(
		retailProjectNumber, 10, 64)
	if err != nil {
		log.Fatalf("Invalid project number: %q, %v", retailProjectNumber, err)
	}
	if err := environmentVariables.validate(); err != nil {
		log.Fatalf("Environments have not been set properly: %v", err)
	}
}

// IngestUserEvents collects GA4 data from BQ and ingests it to the retail API.
func IngestUserEvents(w http.ResponseWriter, r *http.Request) {
	ingestUserEvents(w, r)
}

func ingestUserEvents(w io.Writer, r *http.Request) {
	ctx := context.Background()
	// Init log writer.
	var lw logWriter
	lw.Writer = w
	// Initializes log.
	var err error
	lw.Client, err = logging.NewClient(
		ctx, environmentVariables.MetadataProjectID)

	if err != nil {
		lw.logErrors(fmt.Sprintf("failed to create log client: %v", err))
	} else {
		defer lw.Client.Close()
		lw.ErrLogger = lw.Client.Logger(
			environmentVariables.TaskName).StandardLogger(logging.Error)
		lw.WarningLogger = lw.Client.Logger(
			environmentVariables.TaskName).StandardLogger(logging.Warning)
	}

	var ingester userEventIngester
	ingester.writer = w
	if err := json.NewDecoder(r.Body).Decode(&ingester); err != nil {
		lw.logErrors(fmt.Sprintf("failed to parse body: %v", err))
		return
	}

	// Checks parameters.
	if err := ingester.valid(); err != nil {
		lw.logErrors(fmt.Sprintf("invalid arguments: %v", err))
		return
	}
	// Converts parameters to query parameters.
	ingester.generateQueryParameter()
	fmt.Fprintf(w, "Parameters are OK: %v.\n", ingester)
	statements := ingester.generateSQLStatements()

	// Queries BQ tables.
	rowCollections, err := query(ctx, ingester.BQProjectID, statements)
	if err != nil {
		lw.logErrors(fmt.Sprintf("failed to query database: %v", err))
		return
	}
	var lastSuccessNumbers []int
	var lastRetrievedNumbers []int
	// Ingests user events.
	for _, rows := range rowCollections {
		totalNumber, ingestedNumber, err := ingester.ingestResults(ctx, rows)
		if err != nil {
			lw.logErrors(fmt.Sprintf("failed to print results: %v", err))
			return
		}
		lastSuccessNumbers = append(lastSuccessNumbers, ingestedNumber)
		lastRetrievedNumbers = append(lastRetrievedNumbers, totalNumber)
	}
	lw.logWarnings(fmt.Sprintf(
		"Ingest success numbers:%v, total:%v, statements:%v",
		lastSuccessNumbers, lastRetrievedNumbers, statements))
}

// queryParameter defines the parameters needed when querying BigQuery
// databases.
type queryParameter struct {
	// Tables that contains user events. In general cases, TableNames has a single
	// entity, while it has 2 entities if the time is close to 00:00:00.
	TableNames []string
	// StartTimestamp specifies the earliest time of user events.
	StartTimestamp int64 `json:"StartTimestamp"`
	// EndTimestamp specifies the latest time of user events.
	EndTimestamp int64 `json:"EndTimestamp"`
}

type logWriter struct {
	Client        *logging.Client
	ErrLogger     *log.Logger
	WarningLogger *log.Logger
	Writer        io.Writer
}

func (lw *logWriter) logErrors(errorMessage string) {
	if lw.ErrLogger != nil {
		lw.ErrLogger.Println(errorMessage)
	}
	fmt.Fprintln(lw.Writer, errorMessage)
}

func (lw *logWriter) logWarnings(errorMessage string) {
	if lw.WarningLogger != nil {
		lw.WarningLogger.Println(errorMessage)
	}
	fmt.Fprintln(lw.Writer, errorMessage)
}

func (ingester *userEventIngester) generateQueryParameter() error {
	// The end time of a collection.
	ct := time.Now()
	tables := []string{"events_intraday_*"}
	duration := time.Second * time.Duration(ingester.DurationInSeconds)
	// There may be multiple tables if the DebugCollectTime parameter is
	// specified. Historical data is stored in different tables named by date.
	if ingester.debugMode() {
		var err error
		ct, err = time.Parse("20060102150405", ingester.DebugCollectTime)
		if err != nil {
			return fmt.Errorf(
				"Failed to parse DebugCollectTime %q: %v",
				ingester.DebugCollectTime, err)
		}
		tables = generateTableName(ct, duration)
	}
	for _, t := range tables {
		fullname := fmt.Sprintf(
			"%s.%s.%s", ingester.BQProjectID, ingester.BQDatasetID, t)
		ingester.queryParameter.TableNames = append(
			ingester.queryParameter.TableNames, fullname)
	}
	ingester.queryParameter.StartTimestamp = ct.Add(
		-(duration + time.Second)).UnixNano() / 1000
	ingester.queryParameter.EndTimestamp = ct.UnixNano() / 1000
	return nil
}

func generateTableName(t time.Time, duration time.Duration) []string {
	start := t.Add(-duration)
	// Mon Jan 2 15:04:05 MST 2006
	ret := []string{fmt.Sprintf("events_%s", t.Format("20060102"))}
	if start.YearDay() != t.YearDay() {
		ret = append(ret, fmt.Sprintf("events_%s", start.Format("20060102")))
	}
	return ret
}

var supportedEventNames = []string{
	"add_to_cart", "purchase", "view_search_results", "view_item"}

func generateEventNamesBlock() string {
	var ret strings.Builder
	ret.WriteString("(")
	for i, name := range supportedEventNames {
		if i != 0 {
			ret.WriteString(" or ")
		}
		ret.WriteString(fmt.Sprintf("event_name='%s'", name))
	}
	ret.WriteString(")")
	return ret.String()
}

func (ingester *userEventIngester) generateSQLStatements() []string {
	var res []string
	for _, t := range ingester.queryParameter.TableNames {
		sqlStatement := fmt.Sprintf(
			"SELECT * FROM `%s` where event_timestamp >= %d and event_timestamp < %d and %s ",
			t, ingester.queryParameter.StartTimestamp,
			ingester.queryParameter.EndTimestamp, generateEventNamesBlock())
		res = append(res, sqlStatement)
	}
	return res
}

// query returns a row iterator suitable for reading query results.
func query(ctx context.Context, BQProjectID string, statements []string) (
	[]*bigquery.RowIterator, error) {
	client, err := bigquery.NewClient(ctx, BQProjectID)
	if err != nil {
		return nil, fmt.Errorf("failed to create bigquery client: %v", err)
	}
	defer client.Close()
	ret := []*bigquery.RowIterator{}
	for _, s := range statements {
		query := client.Query(s)
		ri, err := query.Read(ctx)
		if err != nil {
			return nil, err
		}
		ret = append(ret, ri)
	}
	return ret, nil
}

const userEventRequestFormat = "https://retail.googleapis.com/v2alpha/projects/%d/locations/global/catalogs/default_catalog/userEvents:collect?key=%s&userEvent=&raw_json=%s&prebuilt_rule=%s"

func ingestRetailUserEventRawText(ctx context.Context, w io.Writer, projectNumber int64, key string, rawText string, rule string) error {
	fmt.Fprintf(w, "ingesting:\n%v\n", rawText)

	request := fmt.Sprintf(userEventRequestFormat, projectNumber, key, url.QueryEscape(rawText), rule)

	resp, err := http.Get(request)
	if err != nil {
		return fmt.Errorf("failed to send CollectUserEvent request %s: %v", request, err)
	}
	if resp.StatusCode != 200 {
		return fmt.Errorf("failed to ingest through CollectUserEvent %s: %v", request, resp)
	}
	return nil
}
