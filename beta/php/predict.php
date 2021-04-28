<?php
$APIKEY = "";
$PROJECT = "";

$visitorId = json_encode(crypt($SESSIONID,'XYZ123')); // Customize to pass in your sessionid

$ip = json_encode($_SERVER['REMOTE_ADDR']);
$ua = json_encode($_SERVER['HTTP_USER_AGENT']);
$ua = preg_replace('/[[:^print:]]/', '', $ua);
if ($ua == "") {
    $ua = '""';
}

$productid = "54321";  // Or pass in as a url param

$num_results = 10;

// Choose model/placement
$pdp_model = true;
$placementId = "product_detail";
$eventType = "detail-page-view";
//$homepage_model = true;
//$placementId = "home_page";
//$eventType = "home-page-view";

// don't call predict for bots
$bots = "bot|spider|crawler|indexer|fetcher|explorer|jeeves|ia_archiver|ShopWiki|wiceler|yanga|dotnetdotcom|yandex|archive\.org|ScoutJet|Netseer|OpenLinkProfiler|ShopperTom|Pinterest\/|Nutch|WeSEE|AdmantX|Mediapartners-Google|pricepi\.com|MegaIndex\.ru|SEOkick|G\-i\-g\-a\-b\-o\-t|adaptive\.php|qwant\.com|Barkrowler|python|curl|libwww|UptimeCheck|SEMrush|Zonelenny|Jetty|Dalvick|Apache|HttpClient|java|Google-Ads|Dispatch|AppEngine|EasyBib|^Foo$|ltx71|^Chrome$|kinja-links|Microsoft Office|Liner\/|Wordpress|scrapy|SMUrl|Faraday|Citoid|facebook|externalhit|^Ruby$|Daum\/|linkpad";

if (preg_match("/($bots)/i",$ua)) {
    return;
}

$data = <<<EOD
{
  "filter": "filterOutOfStockItems",
  "userEvent": {
    "eventType": "$eventType",
    "userInfo": {
        "visitorId": $visitorId,
EOD;

if ($logged_userid) {  // Customize to use your logged-in userid, if available.  Hash if necessary (no PII like email address)
    $data .= "\"userId\": " . json_encode($logged_userid) . ",";
}
        
$data .= <<<EOD
"ipAddress": $ip,
"userAgent": $ua
},
"eventDetail": {},
EOD;

if ($pdp_model) {
    $data .= <<<EOD
    "productEventDetail": {
        "productDetails": [{
            "id": "$productid",
            "currencyCode": "USD"
        }]
    }
EOD;
}

$data .= "
    },
}";

$url = "https://recommendationengine.googleapis.com/v1beta1/projects/$PROJECT/locations/global/catalogs/default_catalog/eventStores/default_event_store/placements/$placementId:predict?key=$APIKEY";

if (!$ch) {
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "POST");
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type: application/json'));                                                                                                                   
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 1);  //1 sec timeout for connect
    curl_setopt($ch, CURLOPT_TIMEOUT, 3);  //3 sec timeout for entire request
}

curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_POSTFIELDS, $data);

$return = curl_exec($ch);
$errno = curl_errno($ch);
$info = curl_getinfo($ch);

if ($errno != 0 || $info['http_code'] != "200") {
    print("Recommendations Error: " . $return . "\n" . "ua: $ua\ndata:\n" . $data . "\n" . print_r($info,true) . "\n" . print_r($_SERVER,true));
    return;
}

$json = json_decode($return);

$rec_token = $json->recommendationToken;

$ids = "";

$idcount = 0;

foreach ((array)$json->results as $item) {
    $id = $item->id;
    print "Recommendation: $id<br/>\n";
}
        
?>
