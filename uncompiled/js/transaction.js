
goog.provide('elevate300.Transaction');

goog.require('goog.dom');
goog.require('goog.events');


/**
 * Creates the controller js for the /transaction page.
 *  
 * @constructor
 */
elevate300.Transaction = function() {
	window.console.log("Make a new transaction")
};

//goog.events.listen(window, goog.events.EventType.LOAD, function() {
//		new elevate300.Transaction();
//});
goog.exportSymbol('elevate300.Transaction', elevate300.Transaction);