
/**
 * @fileoverview Controller for the Leaderboard page.
 *   
 * @author fisherds@gmail.com (Dave Fisher)
 */

goog.provide('elevate300.Leaderboard');

goog.require('goog.debug.Console');
goog.require('goog.debug.LogManager');
goog.require('goog.debug.Logger');
goog.require('goog.dom');
goog.require('goog.events');
goog.require('goog.events.EventHandler');
goog.require('goog.ui.Control');
goog.require('goog.style');


/**
 * Creates the controller js for the Leaderboard page.
 *  
 * @constructor
 */
elevate300.Leaderboard = function() {
  
  /**
   * Event handler that will bind all callbacks to this.
   * @type {goog.events.EventHandler}
   * @private
   */
  this.eventHandler_ = new goog.events.EventHandler(this);
  
  this.init_();
};
goog.exportSymbol('elevate300.Leaderboard', elevate300.Leaderboard);



/**
 * Logger for this class.
 * @type {goog.debug.Logger}
 */
elevate300.Leaderboard.prototype.logger =
    goog.debug.Logger.getLogger('elevate300.Leaderboard');


/**
 * Initialize the Leaderboard controller.
 * @private
 */
elevate300.Leaderboard.prototype.init_ = function() {  
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
elevate300.Leaderboard.prototype.handleResize_ = function(e) {
  this.resizeElements_();
};


/**
 * Resize the elements on the screen based on the window width.
 * Allow a few margins
 * @private
 */
elevate300.Leaderboard.prototype.resizeElements_ = function() {
  var fillBars = goog.dom.getElementsByClass('fill-bar');
  var totalPanes = goog.dom.getElementsByClass('total-value');
  for (var i = 0; i < fillBars.length; i++) {
    var fillBar = fillBars[i];
    var value = parseInt(totalPanes[i].innerHTML, 10);
    var percentage = value / 300 * 100;
    goog.style.setStyle(fillBar, 'width', percentage + '%');
    goog.style.setStyle(fillBar, '-webkit-transition',
        'width 1500ms ease-in-out ' + ((i+2)*300) + 'ms');
    goog.style.setStyle(fillBar, 'background', 
        '-webkit-gradient(linear, left top, left bottom, ' +
        'color-stop(0, hsl(' + (value/2) + ', 60%, 50%)), color-stop(0.8, #DDD))');
    }
};

