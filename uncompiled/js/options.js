
/**
 * @fileoverview Controller for the Options page.
 *   
 * @author fisherds@gmail.com (Dave Fisher)
 */

goog.provide('elevate300.Options');

goog.require('goog.debug.Console');
goog.require('goog.debug.LogManager');
goog.require('goog.debug.Logger');
goog.require('goog.dom');
goog.require('goog.events');
goog.require('goog.events.EventHandler');
goog.require('goog.ui.Control');
goog.require('goog.style');


/**
 * Creates the controller js for the Options page.
 *  
 * @constructor
 */
elevate300.Options = function() {
  
  /**
   * Event handler that will bind all callbacks to this.
   * @type {goog.events.EventHandler}
   * @private
   */
  this.eventHandler_ = new goog.events.EventHandler(this);
  
  this.init_();
};
goog.exportSymbol('elevate300.Options', elevate300.Options);


/**
 * Logger for this class.
 * @type {goog.debug.Logger}
 */
elevate300.Options.prototype.logger =
    goog.debug.Logger.getLogger('elevate300.Options');


/**
 * Initialize the Options controller.
 * @private
 */
elevate300.Options.prototype.init_ = function() {
  
  // Set up a logger.
  goog.debug.LogManager.getRoot().setLevel(goog.debug.Logger.Level.ALL);
  var logconsole = new goog.debug.Console();
  logconsole.setCapturing(true);
  
  // Listen for window resize events.
  this.eventHandler_.listen(window, goog.events.EventType.RESIZE,
      this.handleResize_);
  
  // Listen for select element changes
  var currentTripSelect = goog.dom.getElement('current-trip-select');
  currentTripSelect.onchange = goog.bind(this.currentTripSelectChanged_, this);
  var editTripSelect = goog.dom.getElement('edit-trip-select');
  editTripSelect.onchange = goog.bind(this.editTripSelectChanged_, this);

  // Listen for the new trip button.
  var submitControl = new goog.ui.Control('');
  submitControl.setSupportedState(goog.ui.Component.State.FOCUSED, false);
  submitControl.setSupportedState(goog.ui.Component.State.DISABLED, false);
  submitControl.decorate(goog.dom.getElement('new-trip'));
  this.eventHandler_.listen(submitControl, goog.ui.Component.EventType.ACTION,
      this.newTripButtonHandler_);
  
  this.resizeElements_();
};


/**
 * 
 * @param {goog.events.Event} e
 */
elevate300.Options.prototype.currentTripSelectChanged_ = function(e) {
  var selectElement = /** @type {Element} */ (e.target);
  var selectedIndex = selectElement.options.selectedIndex;
  var selectedText = selectElement.options[selectedIndex].text;
  var selectedValue = selectElement.options[selectedIndex].value;

  this.logger.info("selectedIndex = " + selectedIndex);
  this.logger.info("selectedText = " + selectedText);
  this.logger.info("selectedValue = " + selectedValue);
  //window.location.href='/trip?id=';

  if (selectedIndex != 0) {
    var formEl = goog.dom.getElement('select-current-trip-form');
    formEl.submit();    
  }
};


/**
 * 
 * @param {goog.events.Event} e
 */
elevate300.Options.prototype.editTripSelectChanged_ = function(e) {
  var selectElement = /** @type {Element} */ (e.target);
  var selectedIndex = selectElement.options.selectedIndex;
  var selectedText = selectElement.options[selectedIndex].text;
  var selectedValue = selectElement.options[selectedIndex].value;

  this.logger.info("selectedIndex = " + selectedIndex);
  this.logger.info("selectedText = " + selectedText);
  this.logger.info("selectedValue = " + selectedValue);
  if (selectedIndex != 0) {
    window.location.href='/trip?id=' + selectedValue;
  }
};


/**
 * Handler for the add new trip button.
 * @param {goog.events.Event} e Button click event.
 */
elevate300.Options.prototype.newTripButtonHandler_ = function(e) {
  window.location.href='/trip';
};

/**
 * @param {goog.events.Event} e The event for the window resize.
 * @private
 */
elevate300.Options.prototype.handleResize_ = function(e) {
  this.resizeElements_();
};

/**
 * Resize the elements on the screen based on the window width.
 * Allow a few margins
 * @private
 */
elevate300.Options.prototype.resizeElements_ = function() {
  // Manually resize some elements to fill the screen width.
};
