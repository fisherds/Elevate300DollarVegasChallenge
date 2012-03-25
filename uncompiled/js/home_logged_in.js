
/**
 * @fileOverview Controller for the HomeLoggedIn page.  .
 *   
 * @author fisherds@gmail.com (Dave Fisher)
 */

goog.provide('elevate300.HomeLoggedIn');

goog.require('goog.debug.Console');
goog.require('goog.debug.LogManager');
goog.require('goog.debug.Logger');
goog.require('goog.dom');
goog.require('goog.events');
goog.require('goog.events.EventHandler');
goog.require('goog.ui.Control');
goog.require('goog.style');


/**
 * Creates the controller js for the HomeLoggedIn page.
 *  
 * @constructor
 */
elevate300.HomeLoggedIn = function() {
  
  /**
   * Event handler that will bind all callbacks to this.
   * @type {goog.events.EventHandler}
   * @private
   */
  this.eventHandler_ = new goog.events.EventHandler(this);
  
  this.init_();
};
goog.exportSymbol('elevate300.HomeLoggedIn', elevate300.HomeLoggedIn);



/**
 * Logger for this class.
 * @type {goog.debug.Logger}
 */
elevate300.HomeLoggedIn.prototype.logger =
    goog.debug.Logger.getLogger('elevate300.HomeLoggedIn');


/**
 * Initialize the HomeLoggedIn controller.
 * @private
 */
elevate300.HomeLoggedIn.prototype.init_ = function() {  
  // Set up a logger.
  goog.debug.LogManager.getRoot().setLevel(goog.debug.Logger.Level.ALL);
  var logconsole = new goog.debug.Console();
  logconsole.setCapturing(true);

  // Listen for window resize events.
  this.eventHandler_.listen(window, goog.events.EventType.RESIZE,
      this.handleResize_);


  var innerBoxes = goog.dom.getElementsByClass('inner-box-text');
  for (var i = 0; i < innerBoxes.length; i++) {
    var innerBox = innerBoxes[i];
    var boxControl = new goog.ui.Control('');
    boxControl.setSupportedState(goog.ui.Component.State.FOCUSED, false);
    boxControl.setSupportedState(goog.ui.Component.State.DISABLED, false);
    boxControl.decorate(goog.dom.getElement(innerBox));
    this.eventHandler_.listen(boxControl, goog.ui.Component.EventType.ACTION,
        this.boxControlActionHandler_);
  }
  
  this.resizeElements_();
};


elevate300.HomeLoggedIn.prototype.boxControlActionHandler_ = function(e) {
  var boxTextId = e.target.getElement().id;
  this.logger.info("You just clicked a box with child " + boxTextId);
  window.location.href = "/" + boxTextId;
};

/**
 * @param {goog.events.Event} e The event for the window resize.
 * @private
 */
elevate300.HomeLoggedIn.prototype.handleResize_ = function(e) {
  this.resizeElements_();
};


/**
 * Resize the elements on the screen based on the window width.
 * @private
 */
elevate300.HomeLoggedIn.prototype.resizeElements_ = function() {
  var screenWidth = window.innerWidth;
  var screenHeight = window.innerHeight;
  var leftMargin = (screenWidth - 100) / 2;
  var topMargin = (screenHeight - 300 - 96) / 2 + 196;
  var outerBox = goog.dom.getElementByClass('outer-box');
  goog.style.setStyle(outerBox, 'left', leftMargin + 'px');
  goog.style.setStyle(outerBox, 'top', topMargin + 'px');
  goog.style.setStyle(outerBox, '-webkit-transform', 'rotate(360deg)');
  var innerBoxes = goog.dom.getElementsByClass('inner-box');
  for (var i = 0; i < innerBoxes.length; i++) {
    var innerBox = innerBoxes[i];
    goog.style.setStyle(innerBox, '-webkit-transform', 'rotate(90deg)');
  }

  var leaderBoardEl = goog.dom.getElement('leaderboard');
  goog.style.setStyle(leaderBoardEl, 'left', '0');
  goog.style.setStyle(leaderBoardEl, 'top', '-72px');
  goog.style.setStyle(leaderBoardEl, 'opacity', '1');
  var individualEl = goog.dom.getElement('individual');
  goog.style.setStyle(individualEl, 'left', '-100px');
  goog.style.setStyle(individualEl, 'top', '31px');
  goog.style.setStyle(individualEl, 'opacity', '1');
  var transactionEl = goog.dom.getElement('transaction');
  goog.style.setStyle(transactionEl, 'left', '100px');
  goog.style.setStyle(transactionEl, 'top', '31px');
  goog.style.setStyle(transactionEl, 'opacity', '1');
  var optionsEl = goog.dom.getElement('options');
  goog.style.setStyle(optionsEl, 'left', '0');
  goog.style.setStyle(optionsEl, 'top', '130px');
  goog.style.setStyle(optionsEl, 'opacity', '1');
  
};

