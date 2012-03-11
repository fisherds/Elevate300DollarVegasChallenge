
/**
 * @fileOverview 
 *   
 * @author fisherds@gmail.com (Dave Fisher)
 */

goog.provide('elevate300.NearestCasino');


/**
 *  
 * @constructor
 */
elevate300.NearestCasino = function() {
  
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
elevate300.NearestCasino.prototype.getDistance_ = function(lat1, lat2, lon1, lon2) {
  // From http://www.movable-type.co.uk/scripts/latlong.html
  // Fast close-enough approach
  var R = 6371; // km
  var x = (lon2-lon1) * Math.cos((lat1+lat2)/2);
  var y = (lat2-lat1);
  return Math.sqrt(x*x + y*y) * R;
};