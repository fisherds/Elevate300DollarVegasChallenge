
/**
 * @fileoverview Controller for the Home page when logged in.
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
//  this.eventHandler_.listen(window, goog.events.EventType.RESIZE,
//      this.handleResize_);

  // Decided to only do the animation once and ignore resize events
  // (they caused and iPhone issue)

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
  var HEADER_SIZE = 75;
  var screenWidth = window.innerWidth;
  var screenHeight = window.innerHeight;
  var outerBox = goog.dom.getElementByClass('outer-box');
  var innerBoxes = goog.dom.getElementsByClass('inner-box');
  var innerBoxTexts = goog.dom.getElementsByClass('inner-box-text');
  var actualTextDivs = goog.dom.getElementsByClass('actual-text');
  var leaderBoardEl = goog.dom.getElement('leaderboard');
  var individualEl = goog.dom.getElement('individual');
  var transactionEl = goog.dom.getElement('transaction');
  var optionsEl = goog.dom.getElement('options');
  
  // Turn off animations for the resize event to happen instantly (reset positions)
  goog.style.setStyle(outerBox, '-webkit-transition', '');
  goog.style.setStyle(outerBox, '-webkit-transform', 'rotate(0deg)');
  for (var i = 0; i < innerBoxes.length; i++) {
    var innerBox = innerBoxes[i];
    goog.style.setStyle(innerBox, '-webkit-transition', '');
    goog.style.setStyle(innerBox, '-webkit-transform', 'rotate(0deg)');
  }
  for (var i = 0; i < innerBoxTexts.length; i++) {
    var innerBoxText = innerBoxTexts[i];
    goog.style.setStyle(innerBoxText, '-webkit-transition', '');
    goog.style.setStyle(innerBoxText, 'opacity', '0');
  }
  goog.style.setStyle(leaderBoardEl, 'top', '0');
  goog.style.setStyle(individualEl, 'left', '0');
  goog.style.setStyle(transactionEl, 'left', '0');
  goog.style.setStyle(optionsEl, 'top', '0');
  
  // Resize the boxes and center
  var maxWidth = (screenWidth - 20) / 3;
  var maxHeight = (screenHeight - HEADER_SIZE - 20) / 3;
  var boxSize = Math.min(maxWidth, maxHeight, 100);
  var boxSizeStr = boxSize + 'px';
  var leftMargin = (screenWidth - boxSize) / 2;
  var topMargin = (screenHeight - 3 * boxSize - HEADER_SIZE) / 2 + (boxSize + HEADER_SIZE);
  goog.style.setStyle(outerBox, 'left', leftMargin + 'px');
  goog.style.setStyle(outerBox, 'top', topMargin + 'px');
  goog.style.setStyle(outerBox, 'width', boxSizeStr);
  goog.style.setStyle(outerBox, 'height', boxSizeStr);
  for (var i = 0; i < innerBoxes.length; i++) {
    var innerBox = innerBoxes[i];
    goog.style.setStyle(innerBox, 'width', boxSizeStr);
    goog.style.setStyle(innerBox, 'height', boxSizeStr);
  }
  for (var i = 0; i < innerBoxTexts.length; i++) {
    var innerBoxText = innerBoxTexts[i];
    goog.style.setStyle(innerBoxText, 'width', boxSizeStr);
    goog.style.setStyle(innerBoxText, 'height', boxSizeStr);
  }
  
  // Resize the font within the boxes
  var fs = 24;
  while(fs > 6) {
    fs--;
    var everyoneFits = true;
    for (var i = 0; i < actualTextDivs.length; i++) {
      goog.style.setStyle(actualTextDivs[i], 'font-size', fs + 'px');
//      this.logger.info("Box " + i + " has width = " + actualTextDivs[i].offsetWidth + " needs to be " + boxSize);
      if (actualTextDivs[i].offsetWidth > boxSize + 1) {
        everyoneFits = false;
      }
    }
    if (everyoneFits) {
      break;
    }
  }
  fs--;
  for (var i = 0; i < actualTextDivs.length; i++) {
    goog.style.setStyle(actualTextDivs[i], 'font-size', fs + 'px');
  }

  // Turn animations back on and do some transforms
  goog.style.setStyle(outerBox, '-webkit-transition', 'all 1300ms ease-in-out 300ms');
  goog.style.setStyle(outerBox, '-webkit-transform', 'rotate(360deg)');
  for (var i = 0; i < innerBoxes.length; i++) {
    var innerBox = innerBoxes[i];
    goog.style.setStyle(innerBox, '-webkit-transition', 'all 1000ms ease-in-out 600ms');
    goog.style.setStyle(innerBox, '-webkit-transform', 'rotate(90deg)');
  }
  for (var i = 0; i < innerBoxTexts.length; i++) {
    var innerBoxText = innerBoxTexts[i];
    goog.style.setStyle(innerBoxText, '-webkit-transition', 'all 1000ms ease-in-out 1300ms');
    goog.style.setStyle(innerBoxText, 'opacity', '1');
  }
  goog.style.setStyle(leaderBoardEl, 'top', '-' + (boxSize+2) + 'px');
  goog.style.setStyle(individualEl, 'left', '-' + boxSizeStr);
  goog.style.setStyle(transactionEl, 'left', boxSizeStr);
  goog.style.setStyle(optionsEl, 'top', boxSizeStr);
};

