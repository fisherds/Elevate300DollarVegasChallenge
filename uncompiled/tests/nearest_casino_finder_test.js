
/**
 * @fileoverview Unit tests for the uncompiled/js/nearest_casino.js file.
 *
 * @author fisherds@gmail.com (Dave Fisher)
 */

var nearestCasinoFinder = elevate300.NearestCasinoFinder.getInstance();

function setUp() {
  
}

function testGetDistance() {
  // Got result from http://www.movable-type.co.uk/scripts/latlong.html
  // Got location of trop from http://itouchmap.com/latlong.html
  var caAptLat = 37.395849;
  var caAptLong = -122.09378;
  var tropLat = 36.0998;
  var tropLong = -115.1722;
  
  assertRoughlyEquals("Missed known distance", 633.1,
      nearestCasinoFinder.getDistance_(caAptLat, tropLat, caAptLong, tropLong),
      0.1);  
}