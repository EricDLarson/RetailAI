<?php

// Call Retail API completeQuery with 'term'
// Return array of suggestions for jQuery example

require '/home/ericl/src/libs/vendor/autoload.php';

use Google\ApiCore\ApiException;
use Google\Cloud\Retail\V2\CompleteQueryResponse;
use Google\Cloud\Retail\V2\CompletionServiceClient;


$TERM = $_GET['term'];

$PROJECT = "[YOUR PROJECT #]";
$DATASET = 'cloud-retail';  // cloud-retail or user-data

// Create a client.
$completionServiceClient = new CompletionServiceClient([
  'credentials' => '[YOUR JSON KEY FILE]',  // or use application default credentials
]);

$formattedCatalog = CompletionServiceClient::catalogName($PROJECT, 'global', 'default_catalog');

// Call the API and handle any network failures.
try {
/** @var CompleteQueryResponse $response */
  $response = $completionServiceClient->completeQuery($formattedCatalog, $TERM, ['dataset' => $DATASET]);
  $suggestions = $response->getCompletionResults();
  $results = count($suggestions);
  
  print "[";
  for ($i = 0; $i < $results; $i++) {
    printf("\"%s\"", $suggestions[$i]->getSuggestion());
    if ($i < $results-1) {
      print ",";
    }
  }
  print "]";
  //printf($response->serializeToJsonString());
} catch (ApiException $ex) {
  printf('Call failed with message: %s' . PHP_EOL, $ex->getMessage());
}

?>
