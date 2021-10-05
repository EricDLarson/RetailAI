const encodeUriComponent = require('encodeUriComponent');
const generateRandom = require('generateRandom');
const getCookieValues = require('getCookieValues');
const getEventData = require('getEventData');
const logToConsole = require('logToConsole');
const makeString = require('makeString');
const sendHttpGet = require('sendHttpGet');
const setCookie = require('setCookie');
const json = require('JSON');
const makeNumber = require('makeNumber');
const getType = require('getType');
const VISITOR_ID_COOKIE = '_ga';
const MAX_USER_ID = 1000000000;

  /**
   * Transform an GA4 event to Recommendations AI public beta event
   * proto. The enhanced ecommerce user event is represented via a list of
   * ecommerce products and top level metadata such as revenue.
   *
   * @param {?string} eventType event type of the user event. eg:
   *    'purchase-complete',  'add-to-cart'
   *  @param {!Object} ecommerceData An object of action fields related with
   *     the user event.
   * @param {?string} currencyCode A three-character ISO-4217 code. If this is
   *     not set, the currency code is set as USD by default.
   * @return {!Object} An object representation of Recommendations AI public
   *     proto.
   */
  function transformGA4EventToCloudRetail(
      eventType, currencyCode) {
    // Set event type.
    let userEvent = {'eventType': eventType};
    let products = getEventData('items');
    if (getType(products) !== 'array') {
      return userEvent;
    }
    logToConsole(userEvent);
    let productDetails = [];

    /**
     * Helper function to add product features into categoricalFeatures or
     * NumericalFeatures depends on feature value type. Currently only string
     * and number are supported.
     *
     * @param {!Array<!Object<string, ?>>} productList A list of products, each
     *     is an Object.
     */
    const addProductToProductDetails = (productList) => {
      for (let j = 0; j < productList.length; j++) {
        let ecommerceProduct = productList[j];
        logToConsole(ecommerceProduct);
        let productDetail = {'product': {}};
       for (let key in ecommerceProduct) {
          if (key === 'item_id') {
            productDetail.product.id = makeString(ecommerceProduct[key]);
          } else if (key === 'quantity') {
            if (ecommerceProduct[key] !== '') {
              productDetail.quantity = ecommerceProduct[key];
            }
          }
       }
        // Push back product if the product id is defined.
        if (productDetail.product.id !== undefined) {
          if (productDetail.quantity === undefined) {
            productDetail.quantity = 1;
          }
          logToConsole(productDetail);
          productDetails.push(productDetail);
        }
      }
    };

    const createTransactionInfo = () => {
       const purchaseTransaction = {};
       var keys = ['transaction_id', 'value', 'tax', 'shipping'];
       for (let key of keys) {
        const value = getEventData(key);
        if (key === 'items') {
          return;
        }
        if (key === 'transaction_id') {
          purchaseTransaction.id = value;
        } else if (key === 'value') {
          if (value !== '') {
            purchaseTransaction.revenue = makeNumber(value);
          }
        } else if (key === 'tax') {
          if (value !== '') {
            purchaseTransaction.tax = makeNumber(value);
          }
        } else if (key === 'shipping') {
          if (value !== '') {
            purchaseTransaction.cost = makeNumber(value);
          }
        }
      }

      if (purchaseTransaction.revenue === undefined) {
        purchaseTransaction.revenue = 0;
      }
      if (purchaseTransaction.currencyCode === undefined) {
        purchaseTransaction.currencyCode = currencyCode || 'USD';
      }
      return purchaseTransaction;
    };
        
        
    logToConsole(userEvent); 
    logToConsole(products);
    addProductToProductDetails(products);
    logToConsole(productDetails);
    userEvent.productDetails = productDetails;
    if (eventType === 'purchase-complete') {
      userEvent.purchaseTransaction = createTransactionInfo();
    }
    return userEvent;
  }

function ingestData(event) {
  logToConsole(event);
   const pageLocation = getEventData('page_location');
   const automlUrl = 'https://retail.googleapis.com/v2' +
        '/projects/' + encodeUriComponent(data.projectNumber) +
        '/locations/global/catalogs/default_catalog' +
        '/userEvents:collect?key=' + encodeUriComponent(data.apiKey) +
        '&uri=' + encodeUriComponent(pageLocation.substring(0, 1500)) +
        '&user_event=' + encodeUriComponent(json.stringify(event));
  
  sendHttpGet(automlUrl, (statusCode) => {
  if (statusCode >= 200 && statusCode < 300) {
    data.gtmOnSuccess();
  } else {
    data.gtmOnFailure();
  }
}); 
}
    

function ingestGA4Data(ecommerceData, eventType) {
  const currencyCode = getEventData('currency');
  let ga4ToRetailMap = {
    'view_item': 'detail-page-view',
    'purchase': 'purchase-complete',
    'add_to_cart': 'add-to-cart'
  };
  if (ga4ToRetailMap[eventType] || 
      ((eventType == 'view_item_list' ||
        eventType === 'view_search_results')  &&         
       data.searchQuery !== undefined &&
       data.searchQuery !== "")) {
    const ga4EventType = (eventType == 'view_item_list' ||
        eventType === 'view_search_results') ? 'search' : ga4ToRetailMap[eventType];
    const cloudRetail = transformGA4EventToCloudRetail(ga4EventType, currencyCode);
    const gaCookiePrefix = data.gaCookiePrefix || "";
    cloudRetail.visitorId = gaCookiePrefix + data.visitorId;
    cloudRetail.attributes = {};
    cloudRetail.attributes.tag = {};
    cloudRetail.attributes.tag.text = ["SGTM"];
    const experimentIds = getCookieValues('_gaexp');
    if (experimentIds.length) {
      cloudRetail.experimentIds = experimentIds;
    }
    if (data.searchQuery !== undefined && data.searchQuery !== "") {
      cloudRetail.searchQuery = data.searchQuery;
    }
    ingestData(cloudRetail);
  } else {
     data.gtmOnSuccess();
  }
  return;
}

// The event name is taken from either the tag's configuration or from the
// event. Configuration data comes into the sandboxed code as a predefined
// variable called 'data'.
const eventName = data.eventName || getEventData('event_name');
ingestGA4Data(data, eventName);
