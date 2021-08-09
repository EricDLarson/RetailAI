<?php

// Example using Retail php client libraries to get prediction results

require 'vendor/autoload.php';

use Google\Cloud\Retail\V2\PredictionServiceClient;
use Google\Cloud\Retail\V2\PredictResponse;
use Google\Cloud\Retail\V2\Product;
use Google\Cloud\Retail\V2\ProductDetail;
use Google\Cloud\Retail\V2\UserEvent;

$predictionClient = new PredictionServiceClient([
  'credentials' => '[your service account key.json file]'
]);

$placement = "projects/[YOUR PROJECT #]/locations/global/catalogs/default_catalog/placements/product_detail";

$product_detail = new ProductDetail([
  'product' => new Product(['id' => '12345']),
  'quantity' => 1
]);

$userEvent = new UserEvent([
  'event_type' => 'detail-page-view',
  'visitor_id' => 'ABCDEFG',
  'product_details' => [
    new ProductDetail([
      'product' => new Product(['id' => '12345']),
      'quantity' => 1
    ])
  ]
]);

$pb_true = new Google\Protobuf\Value();
$pb_true->setBoolValue(true);

try {
  $predictions = $predictionClient->predict($placement, $userEvent, [
    'params' => ['returnProduct' => $pb_true],
    'filter' => 'filterOutOfStockItems'
    ]
  );
} finally {
  $predictionClient->close();
}

$results = $predictions->getResults();

print($results->count() . " Item Id's Returned:");

$iterator = $results->getIterator();
while($iterator->valid()) {
  print($iterator->current()->getId() . "\n");
  
  // With returnProduct=true we can get all the product data
  print_r(json_decode($iterator->current()->serializeToJsonString()));
  
  $iterator->next();
}

?>
