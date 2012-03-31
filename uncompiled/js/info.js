
/**
 * @fileoverview Controller for the Info page.
 *   
 * @author fisherds@gmail.com (Dave Fisher)
 */

goog.provide('elevate300.Info');

goog.require('goog.debug.Console');
goog.require('goog.debug.LogManager');
goog.require('goog.debug.Logger');
goog.require('goog.dom');
goog.require('goog.events');
goog.require('goog.events.EventHandler');
goog.require('goog.ui.Control');
goog.require('goog.style');


/**
 * Creates the controller js for the Info page.
 *  
 * @constructor
 */
elevate300.Info = function() {
  
  /**
   * Event handler that will bind all callbacks to this.
   * @type {goog.events.EventHandler}
   * @private
   */
  this.eventHandler_ = new goog.events.EventHandler(this);
  
  this.init_();
};
goog.exportSymbol('elevate300.Info', elevate300.Info);



/**
 * Logger for this class.
 * @type {goog.debug.Logger}
 */
elevate300.Info.prototype.logger =
    goog.debug.Logger.getLogger('elevate300.Info');


/**
 * Initialize the Info controller.
 * @private
 */
elevate300.Info.prototype.init_ = function() {  
  // Set up a logger.
  goog.debug.LogManager.getRoot().setLevel(goog.debug.Logger.Level.ALL);
  var logconsole = new goog.debug.Console();
  logconsole.setCapturing(true);

  // Listen for window resize events.
  this.eventHandler_.listen(window, goog.events.EventType.RESIZE,
      this.handleResize_);

  this.resizeElements_();
};


/**
 * @param {goog.events.Event} e The event for the window resize.
 * @private
 */
elevate300.Info.prototype.handleResize_ = function(e) {
  this.resizeElements_();
};


/**
 * Resize the elements on the screen based on the window width.
 * Allow a few margins
 * @private
 */
elevate300.Info.prototype.resizeElements_ = function() {
  var screenWidth = window.innerWidth;
  if (screenWidth < 560) {
    this.logger.info("Resize the iframe to width = " + screenWidth);
    var videoIframe = goog.dom.getElement('video-iframe');
    videoIframe.width = screenWidth;
    videoIframe.height = screenWidth / 16 * 9;
  }
};

