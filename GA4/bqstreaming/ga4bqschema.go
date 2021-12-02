package ingestuserevents

import "cloud.google.com/go/bigquery"

// GA4BQRow represents GA4 BQ schema.
type GA4BQRow struct {
	EventDate               bigquery.NullString  `bigquery:"event_date,nullable" json:"event_date,omitempty"`
	EventTimestamp          bigquery.NullInt64   `bigquery:"event_timestamp,nullable" json:"event_timestamp,omitempty"`
	EventName               bigquery.NullString  `bigquery:"event_name,nullable" json:"event_name,omitempty"`
	EventParams             []EventParams        `bigquery:"event_params,nullable" json:"event_params,omitempty"`
	EventValueInUsd         bigquery.NullFloat64 `bigquery:"event_value_in_usd,nullable" json:"event_value_in_usd,omitempty"`
	EventBundleSequenceID   bigquery.NullInt64   `bigquery:"event_bundle_sequence_id" json:"event_bundle_sequence_id,omitempty"`
	UserPseudoID            bigquery.NullString  `bigquery:"user_pseudo_id" json:"user_pseudo_id,omitempty"`
	PrivacyInfo             *PrivacyInfo         `bigquery:"privacy_info" json:"privacy_info,omitempty"`
	UserFirstTouchTimestamp bigquery.NullInt64   `bigquery:"user_first_touch_timestamp" json:"user_first_touch_timestamp,omitempty"`
	UserLtv                 *UserLtv             `bigquery:"user_ltv" json:"user_ltv,omitempty"`
	Device                  *Device              `bigquery:"device" json:"device,omitempty"`
	Geo                     *Geo                 `bigquery:"geo" json:"geo,omitempty"`
	TrafficSource           *TrafficSource       `bigquery:"traffic_source" json:"traffic_source,omitempty"`
	StreamID                bigquery.NullString  `bigquery:"stream_id" json:"stream_id,omitempty"`
	Platform                bigquery.NullString  `bigquery:"platform" json:"platform,omitempty"`
	Ecommerce               *Ecommerce           `bigquery:"ecommerce" json:"ecommerce,omitempty"`
	Items                   []Items              `bigquery:"items" json:"items,omitempty"`
}

// Value is a struct in GA4 schema.
type Value struct {
	StringValue bigquery.NullString  `bigquery:"string_value" json:"string_value,omitempty"`
	IntValue    bigquery.NullInt64   `bigquery:"int_value" json:"int_value,omitempty"`
	FloatValue  bigquery.NullFloat64 `bigquery:"float_value" json:"float_value,omitempty"`
	DoubleValue bigquery.NullFloat64 `bigquery:"double_value" json:"double_value,omitempty"`
}

// EventParams is a struct in GA4 schema.
type EventParams struct {
	Key   bigquery.NullString `bigquery:"key" json:"key,omitempty"`
	Value *Value              `bigquery:"value" json:"value,omitempty"`
}

// PrivacyInfo is a struct in GA4 schema.
type PrivacyInfo struct {
	UsesTransientToken bigquery.NullString `bigquery:"uses_transient_token" json:"uses_transient_token,omitempty"`
}

// UserLtv is a struct in GA4 schema.
type UserLtv struct {
	Revenue  bigquery.NullFloat64 `bigquery:"revenue" json:"revenue,omitempty"`
	Currency bigquery.NullString  `bigquery:"currency" json:"currency,omitempty"`
}

// WebInfo is a struct in GA4 schema.
type WebInfo struct {
	Browser        bigquery.NullString `bigquery:"browser" json:"browser,omitempty"`
	BrowserVersion bigquery.NullString `bigquery:"browser_version" json:"browser_version,omitempty"`
	Hostname       bigquery.NullString `bigquery:"hostname" json:"hostname,omitempty"`
}

// Device is a struct in GA4 schema.
type Device struct {
	Category               bigquery.NullString `bigquery:"category" json:"category,omitempty"`
	MobileBrandName        bigquery.NullString `bigquery:"mobile_brand_name" json:"mobile_brand_name,omitempty"`
	MobileModelName        bigquery.NullString `bigquery:"mobile_model_name" json:"mobile_model_name,omitempty"`
	OperatingSystem        bigquery.NullString `bigquery:"operating_system" json:"operating_system,omitempty"`
	OperatingSystemVersion bigquery.NullString `bigquery:"operating_system_version" json:"operating_system_version,omitempty"`
	Language               bigquery.NullString `bigquery:"language" json:"language,omitempty"`
	IsLimitedAdTracking    bigquery.NullString `bigquery:"is_limited_ad_tracking" json:"is_limited_ad_tracking,omitempty"`
	WebInfo                *WebInfo            `bigquery:"web_info" json:"web_info,omitempty"`
}

// Geo is a struct in GA4 schema.
type Geo struct {
	Continent    bigquery.NullString `bigquery:"continent" json:"continent,omitempty"`
	Country      bigquery.NullString `bigquery:"country" json:"country,omitempty"`
	Region       bigquery.NullString `bigquery:"region" json:"region,omitempty"`
	City         bigquery.NullString `bigquery:"city" json:"city,omitempty"`
	SubContinent bigquery.NullString `bigquery:"sub_continent" json:"sub_continent,omitempty"`
	Metro        bigquery.NullString `bigquery:"metro" json:"metro,omitempty"`
}

// TrafficSource is a struct in GA4 schema.
type TrafficSource struct {
	Name   bigquery.NullString `bigquery:"name" json:"name,omitempty"`
	Medium bigquery.NullString `bigquery:"medium" json:"medium,omitempty"`
	Source bigquery.NullString `bigquery:"source" json:"source,omitempty"`
}

// Ecommerce is a struct in GA4 schema.
type Ecommerce struct {
	TotalItemQuantity    bigquery.NullInt64   `bigquery:"total_item_quantity" json:"total_item_quantity,omitempty"`
	PurchaseRevenueInUsd bigquery.NullFloat64 `bigquery:"purchase_revenue_in_usd" json:"purchase_revenue_in_usd,omitempty"`
	PurchaseRevenue      bigquery.NullFloat64 `bigquery:"purchase_revenue" json:"purchase_revenue,omitempty"`
	ShippingValueInUsd   bigquery.NullFloat64 `bigquery:"shipping_value_in_usd" json:"shipping_value_in_usd,omitempty"`
	ShippingValue        bigquery.NullFloat64 `bigquery:"shipping_value" json:"shipping_value,omitempty"`
	TaxValueInUsd        bigquery.NullFloat64 `bigquery:"tax_value_in_usd" json:"tax_value_in_usd,omitempty"`
	TaxValue             bigquery.NullFloat64 `bigquery:"tax_value" json:"tax_value,omitempty"`
	UniqueItems          bigquery.NullInt64   `bigquery:"unique_items" json:"unique_items,omitempty"`
	TransactionID        bigquery.NullString  `bigquery:"transaction_id" json:"transaction_id,omitempty"`
}

// Items is a struct in GA4 schema.
type Items struct {
	ItemID           bigquery.NullString  `bigquery:"item_id" json:"item_id,omitempty"`
	ItemName         bigquery.NullString  `bigquery:"item_name" json:"item_name,omitempty"`
	ItemBrand        bigquery.NullString  `bigquery:"item_brand" json:"item_brand,omitempty"`
	ItemVariant      bigquery.NullString  `bigquery:"item_variant" json:"item_variant,omitempty"`
	ItemCategory     bigquery.NullString  `bigquery:"item_category" json:"item_category,omitempty"`
	ItemCategory2    bigquery.NullString  `bigquery:"item_category2" json:"item_category2,omitempty"`
	ItemCategory3    bigquery.NullString  `bigquery:"item_category3" json:"item_category3,omitempty"`
	ItemCategory4    bigquery.NullString  `bigquery:"item_category4" json:"item_category4,omitempty"`
	ItemCategory5    bigquery.NullString  `bigquery:"item_category5" json:"item_category5,omitempty"`
	PriceInUsd       bigquery.NullFloat64 `bigquery:"price_in_usd" json:"price_in_usd,omitempty"`
	Price            bigquery.NullFloat64 `bigquery:"price" json:"price,omitempty"`
	Quantity         bigquery.NullInt64   `bigquery:"quantity" json:"quantity,omitempty"`
	ItemRevenueInUsd bigquery.NullFloat64 `bigquery:"item_revenue_in_usd" json:"item_revenue_in_usd,omitempty"`
	ItemRevenue      bigquery.NullFloat64 `bigquery:"item_revenue" json:"item_revenue,omitempty"`
	Coupon           bigquery.NullString  `bigquery:"coupon" json:"coupon,omitempty"`
	Affiliation      bigquery.NullString  `bigquery:"affiliation" json:"affiliation,omitempty"`
	LocationID       bigquery.NullString  `bigquery:"location_id" json:"location_id,omitempty"`
	ItemListID       bigquery.NullString  `bigquery:"item_list_id" json:"item_list_id,omitempty"`
	ItemListName     bigquery.NullString  `bigquery:"item_list_name" json:"item_list_name,omitempty"`
	ItemListIndex    bigquery.NullString  `bigquery:"item_list_index" json:"item_list_index,omitempty"`
	PromotionID      bigquery.NullString  `bigquery:"promotion_id" json:"promotion_id,omitempty"`
	PromotionName    bigquery.NullString  `bigquery:"promotion_name" json:"promotion_name,omitempty"`
	CreativeName     bigquery.NullString  `bigquery:"creative_name" json:"creative_name,omitempty"`
	CreativeSlot     bigquery.NullString  `bigquery:"creative_slot" json:"creative_slot,omitempty"`
}
