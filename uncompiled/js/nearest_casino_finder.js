
/**
 * @fileoverview Finds the distances to the different casinos. 
 *   
 * @author fisherds@gmail.com (Dave Fisher)
 */

goog.provide('elevate300.NearestCasinoFinder');
goog.provide('elevate300.NearestCasinoFinder.Event');

goog.require('goog.array');
goog.require('goog.string');
goog.require('goog.events.Event');
goog.require('goog.events.EventTarget');
goog.require('goog.debug');
goog.require('goog.debug.Logger');
goog.require('goog.json');
goog.require('goog.net.XhrIo');
goog.require('goog.Uri');



/**
 *  
 * @constructor
 * @extends {goog.events.EventTarget}
 */
elevate300.NearestCasinoFinder = function() {
  goog.events.EventTarget.call(this);
};
goog.inherits(elevate300.NearestCasinoFinder, goog.events.EventTarget);
goog.addSingletonGetter(elevate300.NearestCasinoFinder);


/**
 *  
 * @constructor
 * @extends {goog.events.Event}
 */
elevate300.NearestCasinoFinder.Event = function(nearestCasinoFinder, nearestCasinos, allCasinos) {
  goog.events.Event.call(this,
      elevate300.NearestCasinoFinder.EventType.CASINOS_READY,
      nearestCasinoFinder);
  
  this.nearestCasinos = nearestCasinos;
  this.allCasinos = allCasinos;
};
goog.inherits(elevate300.NearestCasinoFinder.Event, goog.events.Event);


/** @enum {string} */
elevate300.NearestCasinoFinder.EventType = {
  CASINOS_READY: goog.events.getUniqueId('casinos-ready')
};


/**
* @type {goog.debug.Logger}
* @protected
*/
elevate300.NearestCasinoFinder.prototype.logger = goog.debug.Logger.getLogger('elevate300.NearestCasinoFinder');


elevate300.NearestCasinoFinder.prototype.getCasinoList = function(latitude, longitude, selectCasino) {
  var googUri = new goog.Uri('casinos');
  var queryData = googUri.getQueryData();
  queryData.add('latitude', latitude);
  queryData.add('longitude', longitude);
  if (!goog.string.isEmpty(selectCasino)) {
    queryData.add('selectcasino', selectCasino);
  }
  goog.net.XhrIo.send(googUri.toString(), goog.bind(this.handleXhrResponse_, this));
};

/** @typedef {{nearest_casinos: Array.<string>, all_casinos: Array.<string>}} */
elevate300.CasinosResponse;


elevate300.NearestCasinoFinder.prototype.handleXhrResponse_ = function(e) {
  var xhr = /** @type {goog.net.XhrIo} */ (e.target);
  if (!xhr.isSuccess()) {
    this.logger.warning("Failed to retrieve a casino list");
    return;
  }
  var jsonResponse = xhr.getResponseText(); 
  
  var response = /** @type {elevate300.CasinosResponse} */ (goog.json.unsafeParse(jsonResponse));
  var nearestCasinos = /** @type {Array.<string>} */ response['nearest_casinos'];
  var allCasinos = /** @type {Array.<string>} */ response['all_casinos'];
  this.dispatchEvent(
      new elevate300.NearestCasinoFinder.Event(
          this, nearestCasinos, allCasinos));
};


/**
 * Returns the distance in km between two GPS locations.
 * 
 * @param {number} lat1
 * @param {number} lat2
 * @param {number} lon1
 * @param {number} lon2
 * @private
 */
elevate300.NearestCasinoFinder.prototype.getDistance_ = function(lat1, lat2, lon1, lon2) {
  // From http://www.movable-type.co.uk/scripts/latlong.html
  // Fast close-enough approach
  
  var R = 6371; // km
  var dLat = (lat2 - lat1) / 180 * Math.PI;
  var dLon = (lon2 - lon1) / 180 * Math.PI;
  lat1 = lat1 / 180 * Math.PI;
  lat2 = lat2 / 180 * Math.PI;

  var a = Math.sin(dLat/2) * Math.sin(dLat/2) +
          Math.sin(dLon/2) * Math.sin(dLon/2) * Math.cos(lat1) * Math.cos(lat2); 
  var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)); 
  return R * c;
};