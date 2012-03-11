
/**
 * @fileOverview Controller for the Trip page.  .
 *   
 * @author fisherds@gmail.com (Dave Fisher)
 */

goog.provide('elevate300.Trip');

goog.require('goog.debug.Console');
goog.require('goog.debug.LogManager');
goog.require('goog.debug.Logger');
goog.require('goog.dom');
goog.require('goog.events');
goog.require('goog.events.EventHandler');
goog.require('goog.ui.Control');
goog.require('goog.style');


/**
 * Creates the controller js for the Trip page.
 *  
 * @constructor
 */
elevate300.Trip = function() {
	
	/**
	 * Event handler that will bind all callbacks to this.
	 * @type {goog.events.EventHandler}
	 * @private
	 */
	this.eventHandler_ = new goog.events.EventHandler(this);
	
  /**
	 * @type {Element}
	 * @private
	 */
  this.blankTemplate_ = null;
  
	this.init_();
};
goog.exportSymbol('elevate300.Trip', elevate300.Trip);


/**
 * Logger for this class.
 * @type {goog.debug.Logger}
 */
elevate300.Trip.prototype.logger =
    goog.debug.Logger.getLogger('elevate300.Trip');


/**
 * Initialize the Trip controller.
 * @private
 */
elevate300.Trip.prototype.init_ = function() {
  
  // Set up a logger.
  goog.debug.LogManager.getRoot().setLevel(goog.debug.Logger.Level.ALL);
  var logconsole = new goog.debug.Console();
  logconsole.setCapturing(true);
  
  // Listen for window resize events.
  this.eventHandler_.listen(window, goog.events.EventType.RESIZE,
      this.handleResize_);
  
  // Listen for the add trip member button.
  var memberControl = new goog.ui.Control('');
  memberControl.setSupportedState(goog.ui.Component.State.FOCUSED, false);
  memberControl.setSupportedState(goog.ui.Component.State.DISABLED, false);
  memberControl.decorate(goog.dom.getElement('add-member-button'));
  this.eventHandler_.listen(memberControl, goog.ui.Component.EventType.ACTION,
      this.memberButtonHandler_);
  
  // Listen for the cancel button.
  var cancelControl = new goog.ui.Control('');
  cancelControl.setSupportedState(goog.ui.Component.State.FOCUSED, false);
  cancelControl.setSupportedState(goog.ui.Component.State.DISABLED, false);
  cancelControl.decorate(goog.dom.getElement('cancel'));
  this.eventHandler_.listen(cancelControl, goog.ui.Component.EventType.ACTION,
      this.cancelButtonHandler_);
  
  // Listen for the submit button.
  var submitControl = new goog.ui.Control('');
  submitControl.setSupportedState(goog.ui.Component.State.FOCUSED, false);
  submitControl.setSupportedState(goog.ui.Component.State.DISABLED, false);
  submitControl.decorate(goog.dom.getElement('submit'));
  this.eventHandler_.listen(submitControl, goog.ui.Component.EventType.ACTION,
      this.submitButtonHandler_);
  
  this.resizeElements_();
  var templateEl = goog.dom.getElement('template');
  this.blankTemplate_ = templateEl.cloneNode(true);
};

/**
 * Handler for the add trip member button.
 * @param {goog.events.Event} e Button click event.
 */
elevate300.Trip.prototype.memberButtonHandler_ = function(e) {
  var templateClone = this.blankTemplate_.cloneNode(true);
  var formEl = goog.dom.getElement('trip-form');
  formEl.appendChild(templateClone);
  this.resizeElements_();
};

/**
 * @param {goog.events.Event} e The event for the cancel button.
 * @private
 */
elevate300.Trip.prototype.cancelButtonHandler_ = function(e) {
  window.history.go(-1);
};


/**
 * @param {goog.events.Event} e The event for the submit button.
 * @private
 */
elevate300.Trip.prototype.submitButtonHandler_ = function(e) {
  var formEl = goog.dom.getElement('trip-form');
  formEl.submit();
};

/**
 * @param {goog.events.Event} e The event for the window resize.
 * @private
 */
elevate300.Trip.prototype.handleResize_ = function(e) {
	this.resizeElements_();
};

/**
 * Resize the elements on the screen based on the window width.
 * Allow a few margins
 * @private
 */
elevate300.Trip.prototype.resizeElements_ = function() {
	// Manually resize some elements to fill the screen width.
	var screenWidth = window.innerWidth;
	var formMargin = 10;
	var formWidth = screenWidth - 2 * formMargin;
	var formEl = goog.dom.getElement('trip-form');
	goog.style.setStyle(formEl, 'margin-left', formMargin + 'px');
	
	var textLabelWidth = 60;
	var textLabels = goog.dom.getElementsByClass('text-input-labels');
	for (var i = 0; i < textLabels.length; i++) {
		goog.style.setStyle(textLabels[i], 'width', textLabelWidth);
	}
	var textBoxWidth = formWidth - textLabelWidth - 8;
	var textBoxes = goog.dom.getElementsByClass('text-input-box');
	for (var i = 0; i < textBoxes.length; i++) {
		goog.style.setStyle(textBoxes[i], 'width', textBoxWidth);
	}
};
