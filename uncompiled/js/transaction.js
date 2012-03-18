
/**
 * @fileOverview Controller for the transaction page.  .
 *   
 * @author fisherds@gmail.com (Dave Fisher)
 */

goog.provide('elevate300.Transaction');

goog.require('goog.debug.Console');
goog.require('goog.debug.LogManager');
goog.require('goog.debug.Logger');
goog.require('goog.dom');
goog.require('goog.events');
goog.require('goog.events.EventHandler');
goog.require('goog.ui.Control');
goog.require('goog.ui.Select');
goog.require('goog.style');


/**
 * Creates the controller js for the transaction page.
 *  
 * @constructor
 */
elevate300.Transaction = function() {
	
	/**
	 * Event handler that will bind all callbacks to this.
	 * @type {goog.events.EventHandler}
	 * @private
	 */
	this.eventHandler_ = new goog.events.EventHandler(this);
	
	this.init_();
};
goog.exportSymbol('elevate300.Transaction', elevate300.Transaction);


/**
 * Logger for this class.
 * @type {goog.debug.Logger}
 */
elevate300.Transaction.prototype.logger =
    goog.debug.Logger.getLogger('elevate300.Transaction');


/**
 * Initialize the transaction controller.
 * @private
 */
elevate300.Transaction.prototype.init_ = function() {
  
  // Set up a logger.
  goog.debug.LogManager.getRoot().setLevel(goog.debug.Logger.Level.ALL);
  var logconsole = new goog.debug.Console();
  logconsole.setCapturing(true);

  // Listen for window resize events.
  this.eventHandler_.listen(window, goog.events.EventType.RESIZE,
      this.handleResize_);
  
  // Listen for users selecting the 'Other' game option
  var gamePlayedSelect = goog.dom.getElement('game-played-select');
  gamePlayedSelect.onchange = goog.bind(this.gameChanged_, this);

  // Listen for the cancel button.
  var cancelControl = new goog.ui.Control('');
  cancelControl.setSupportedState(goog.ui.Component.State.FOCUSED, false);
  cancelControl.setSupportedState(goog.ui.Component.State.DISABLED, false);
  cancelControl.decorate(goog.dom.getElement('cancel'));
  this.eventHandler_.listen(cancelControl, goog.ui.Component.EventType.ACTION,
      this.cancelButtonHandler_);
  
  // Listen for the add transaction button.
  var submitControl = new goog.ui.Control('');
  submitControl.setSupportedState(goog.ui.Component.State.FOCUSED, false);
  submitControl.setSupportedState(goog.ui.Component.State.DISABLED, false);
  submitControl.decorate(goog.dom.getElement('submit'));
  this.eventHandler_.listen(submitControl, goog.ui.Component.EventType.ACTION,
      this.submitButtonHandler_);
  
  // Update the location
  if (!window.navigator.geolocation) {
    this.logger.info("No geo location");
  } else {
    window.navigator.geolocation.getCurrentPosition(
        goog.bind(this.locationSuccessHandler_, this),
        goog.bind(this.locationErrorHandler_, this));
  }
  
	this.resizeElements_();
};

/**
 * 
 */
elevate300.Transaction.prototype.locationSuccessHandler_ = function(pos) {
  var latitude = pos.coords.latitude;
  var longitude = pos.coords.longitude;
  this.logger.info("Succesfully found your position");
  this.logger.info("Latitude = " + latitude);
  this.logger.info("Longitude = " + longitude);
  
//  var distanceToMe = this.getDistance_(latitude, 37.3958459, longitude, -122.0937856);
//  this.logger.info("distanceToMe = " + distanceToMe);
  
};

/**
 * 
 */
elevate300.Transaction.prototype.locationErrorHandler_ = function() {
  this.logger.info("Failed to get a location");
};

/**
 * 
 * @param {goog.events.Event} e
 */
elevate300.Transaction.prototype.gameChanged_ = function(e) {
  var selectElement = /** @type {Element} */ (e.target);
  var selectedIndex = selectElement.options.selectedIndex;
  var selectedText = selectElement.options[selectedIndex].text;
  if (selectedText == 'Other') {
    goog.style.setStyle(selectElement, 'display', 'none');
    var gamePlayedText = goog.dom.getElement('game-played-text');
    goog.style.setStyle(gamePlayedText, 'display', 'inline-block');
  }
};



/**
 * @param {goog.events.Event} e The event for the cancel button.
 * @private
 */
elevate300.Transaction.prototype.cancelButtonHandler_ = function(e) {
  this.logger.info("Clicked cancel");
  window.history.go(-1);
};

/**
 * @param {goog.events.Event} e The event for the submit button.
 * @private
 */
elevate300.Transaction.prototype.submitButtonHandler_ = function(e) {
  this.logger.info("Clicked submit");
  var formEl = goog.dom.getElement('transaction-form');
  formEl.submit();
};


/**
 * @param {goog.events.Event} e The event for the window resize.
 * @private
 */
elevate300.Transaction.prototype.handleResize_ = function(e) {
	this.resizeElements_();
};


/**
 * Resize the elements on the screen based on the window width.
 * Allow a few margins
 * @private
 */
elevate300.Transaction.prototype.resizeElements_ = function() {
	// Manually resize some elements to fill the screen width.
  // Once the CSS calc function is standard garbage like this can go into CSS.
	var screenWidth = window.innerWidth;
	var formMargin = 10;
	var formWidth = screenWidth - 2 * formMargin;
	var formEl = goog.dom.getElement('transaction-form');
	goog.style.setStyle(formEl, 'margin-left', formMargin + 'px');
	
	var selectWidth = (formWidth - formMargin) / 2 - 4;
	var emailAddressSelect = goog.dom.getElement('email-address');
	goog.style.setStyle(emailAddressSelect, 'width', selectWidth + 'px');
	
	var challengeTypeSelect = goog.dom.getElement('challenge-type');
	goog.style.setStyle(challengeTypeSelect, 'width', selectWidth + 'px');
	goog.style.setStyle(challengeTypeSelect, 'margin-left', formMargin + 'px');
	
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
	var gamePlayedSelect = goog.dom.getElement('game-played-select');
	goog.style.setStyle(gamePlayedSelect, 'width', textBoxWidth);
};
