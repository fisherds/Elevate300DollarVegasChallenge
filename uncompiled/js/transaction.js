
/**
 * @fileoverview Controller for the transaction page.
 *   
 * @author fisherds@gmail.com (Dave Fisher)
 */

goog.provide('elevate300.Transaction');


goog.require('elevate300.NearestCasinoFinder');
goog.require('goog.debug.Console');
goog.require('goog.debug.LogManager');
goog.require('goog.debug.Logger');
goog.require('goog.dom');
goog.require('goog.dom.classes');
goog.require('goog.events');
goog.require('goog.events.EventHandler');
goog.require('goog.json');
goog.require('goog.ui.AutoComplete.Basic');
goog.require('goog.ui.Control');
goog.require('goog.ui.Select');
goog.require('goog.style');
goog.require('goog.string');


/**
 * Creates the controller js for the transaction page.
 *  
 * @constructor
 */
elevate300.Transaction = function(selectCasino, addOnsUsedStr, allGamesStr) {

  // Set up a logger.
  goog.debug.LogManager.getRoot().setLevel(goog.debug.Logger.Level.ALL);
  var logconsole = new goog.debug.Console();
  logconsole.setCapturing(true);
  
  /**
   * The casino that should be selected for this trip
   * @type {string}
   */
  this.selectCasino = selectCasino;
  
  /**
   * List of casinos for this trip.
   * @type {Array.<elevate300.AddOns>}
   */
  this.addOnsUsed = [];
  if (addOnsUsedStr.length != 0) {
    addOnsUsedStr = addOnsUsedStr.replace(/u&\#39;/g, "'");
    addOnsUsedStr = addOnsUsedStr.replace(/&\#39;/g, "'");
    addOnsUsedStr = addOnsUsedStr.replace(/&quot;/g, '"');
    this.addOnsUsed = /** @type {Array.<elevate300.Casino>} */
        (goog.json.unsafeParse(addOnsUsedStr));    
  }
  
  /**
   * List of games for this trip.
   * @type {Array.<string>}
   */
  this.allGames = [];
  if (allGamesStr.length != 0) {
    addOnsUsedStr = addOnsUsedStr.replace(/u&\#39;/g, "'");
    allGamesStr = allGamesStr.replace(/&\#39;/g, "'");
    allGamesStr = allGamesStr.replace(/&quot;/g, '"');
    this.allGames = /** @type {Array.<string>} */
        (goog.json.unsafeParse(allGamesStr));    
  }
  
	/**
	 * Event handler that will bind all callbacks to this.
	 * @type {goog.events.EventHandler}
	 * @private
	 */
	this.eventHandler_ = new goog.events.EventHandler(this);
	
	this.init_();
};
goog.exportSymbol('elevate300.Transaction', elevate300.Transaction);


/** @typedef {{name: string, latitude: number, longitude: number}} */
elevate300.Casino;


/** @typedef {{email_address: string, challenge_type: number}} */
elevate300.AddOns;


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
  var transactionId = parseInt(goog.dom.getElement('transaction-id').value, 10);
  if (transactionId == 0) {
    transactionId.disabled = true; // Don't send it with the post
    // Listen for changes the might alter the add on button visibility
    var emailAddressSelect = goog.dom.getElement('email-address');
    emailAddressSelect.onchange = goog.bind(this.emailAddressChanged_, this);
    var challengeTypeSelect = goog.dom.getElement('challenge-type');
    challengeTypeSelect.onchange = goog.bind(this.challengeTypeChanged_, this);    
  }
  
  // Listen for window resize events.
  this.eventHandler_.listen(window, goog.events.EventType.RESIZE,
      this.handleResize_);

  // Listen for users selecting the 'Other' casino option
  var casinoSelect = goog.dom.getElement('casino-select');
  casinoSelect.onchange = goog.bind(this.casinoChanged_, this);

  new goog.ui.AutoComplete.Basic(
      this.allGames, document.getElementById('game-played-text'), false);  
  
  // Listen for users selecting the 'Other' game option
  var gamePlayedSelect = goog.dom.getElement('game-played-select');
  gamePlayedSelect.onchange = goog.bind(this.gamePlayedChanged_, this);
  
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
  
  // Listen for the extra button (add on or delete).
  var extraButtonEl = goog.dom.getElement('extra-button');
  var extraButtonControl = new goog.ui.Control('');
  extraButtonControl.setSupportedState(goog.ui.Component.State.FOCUSED, false);
  extraButtonControl.setSupportedState(goog.ui.Component.State.DISABLED, false);
  extraButtonControl.decorate(extraButtonEl);
  
  // Adjust the extra button to become a delete button if necessary
  if (transactionId == 0) {
    this.eventHandler_.listen(extraButtonControl, goog.ui.Component.EventType.ACTION,
        this.addOnButtonHandler_);
  } else {
    // Change the color and text to say Delete
    extraButtonEl.innerHTML = 'Delete';
    goog.dom.classes.addRemove(extraButtonEl, 'whiteButton', 'redButton');
    goog.style.setStyle(extraButtonEl, 'font-size', '22px');
    this.eventHandler_.listen(extraButtonControl, goog.ui.Component.EventType.ACTION,
        this.deleteButtonHandler_);
  }
  
  // Update the location
  if (!window.navigator.geolocation) {
    this.logger.info("No geo location");
  } else {
    window.navigator.geolocation.getCurrentPosition(
        goog.bind(this.locationSuccessHandler_, this),
        goog.bind(this.locationErrorHandler_, this));
  }
  
  
	this.resizeElements_();
	if (transactionId == 0) {
	  this.updateAddOnVisibility_();
	}
};

/**
 * 
 */
elevate300.Transaction.prototype.locationSuccessHandler_ = function(pos) {
  var latitude = pos.coords.latitude;
  var longitude = pos.coords.longitude;
//  this.logger.info("Succesfully found your position");
//  this.logger.info("Latitude = " + latitude);
//  this.logger.info("Longitude = " + longitude);
  var finder = elevate300.NearestCasinoFinder.getInstance();
  
  this.eventHandler_.listen(finder,
      elevate300.NearestCasinoFinder.EventType.CASINOS_READY,
      this.nearestCasinoHandler_);  
  finder.getCasinoList(latitude, longitude, this.selectCasino);
};

/**
 * 
 */
elevate300.Transaction.prototype.locationErrorHandler_ = function() {
  this.logger.info("Failed to get a location");
};


elevate300.Transaction.prototype.nearestCasinoHandler_ = function(e) {
  var casinoEvent = /** @type {elevate300.NearestCasinoFinder.Event} */ (e);
  this.updateCasinoOptions_(casinoEvent.nearestCasinos);
  new goog.ui.AutoComplete.Basic(
      casinoEvent.allCasinos, document.getElementById('casino-text'), false);
};


/**
 * Event handler called when the casino select element changes.
 * @param {Array.<string>} casinoNames List of casino names to add
 * @private
 */
elevate300.Transaction.prototype.updateCasinoOptions_ = function(casinoNames) {
  // Change which input is displayed.
  var casinoSelectEl = goog.dom.getElement('casino-select');
  casinoSelectEl.disabled = false;
  goog.style.setStyle(casinoSelectEl, 'display', 'inline-block');
  var casinoTextEl = goog.dom.getElement('casino-text');
  casinoTextEl.disabled = true;
  goog.style.setStyle(casinoTextEl, 'display', 'none');
  
  casinoSelectEl.options.length=0;  // Remove any casinos if present
  for (var i = 0; i < casinoNames.length; i++) {
    casinoSelectEl.options[i] = new Option(casinoNames[i], casinoNames[i], false, false);
  }
  casinoSelectEl.options[i] = new Option("Other", "Other", false, false);
};


/**
 * Event handler called when the casino select element changes.
 * @param {goog.events.Event} e
 */
elevate300.Transaction.prototype.casinoChanged_ = function(e) {
  var selectElement = /** @type {Element} */ (e.target);
  var selectedIndex = selectElement.options.selectedIndex;
  var selectedText = selectElement.options[selectedIndex].text;
  if (selectedText == 'Other') {
    goog.style.setStyle(selectElement, 'display', 'none');
    selectElement.disabled = true; // Don't send it with the post
    var casinoText = goog.dom.getElement('casino-text');
    casinoText.disabled = false;
    goog.style.setStyle(casinoText, 'display', 'inline-block');
  }
};


/**
 * Event handler called when the game played select element changes.
 * @param {goog.events.Event} e
 */
elevate300.Transaction.prototype.gamePlayedChanged_ = function(e) {
  var selectElement = /** @type {Element} */ (e.target);
  var selectedIndex = selectElement.options.selectedIndex;
  var selectedText = selectElement.options[selectedIndex].text;
  if (selectedText == 'Other') {
    goog.style.setStyle(selectElement, 'display', 'none');
    selectElement.disabled = true; // Don't send it with the post
    var gamePlayedText = goog.dom.getElement('game-played-text');
    gamePlayedText.disabled = false;
    goog.style.setStyle(gamePlayedText, 'display', 'inline-block');
  }
};



/**
 * Event handler called when the cancel button is pressed.
 * @param {goog.events.Event} e The event for the cancel button.
 * @private
 */
elevate300.Transaction.prototype.cancelButtonHandler_ = function(e) {
  this.logger.info("Clicked cancel");
  window.history.go(-1);
};

/**
 * Event handler called when the submit button is pressed.
 * @param {goog.events.Event} e The event for the submit button.
 * @private
 */
elevate300.Transaction.prototype.submitButtonHandler_ = function(e) {
  this.logger.info("Clicked submit");
  var formEl = goog.dom.getElement('transaction-form');
  formEl.submit();
};


/**
 * Event handler called when the add on button is pressed.
 * @param {goog.events.Event} e The event for the submit button.
 * @private
 */
elevate300.Transaction.prototype.addOnButtonHandler_ = function(e) {
  
  // TODO:  Add an "Are you sure dialog box"
  
  var amountEl = goog.dom.getElement('amount');
  amountEl.disabled = true;
  var casinoSelectEl = goog.dom.getElement('casino-select');
  casinoSelectEl.disabled = true;
  var casinoTextEl = goog.dom.getElement('casino-text');
  casinoTextEl.disabled = true;
  var gamePlayedSelectEl = goog.dom.getElement('game-played-select');
  gamePlayedSelectEl.disabled = true;
  var gamePlayedTextEl = goog.dom.getElement('game-played-text');
  gamePlayedTextEl.disabled = true;
  
//  this.logger.info("Clicked use Add on");
  var addOnEl = goog.dom.getElement('is-add-on');
  addOnEl.disabled = false;
  addOnEl.value = 'True';
  var formEl = goog.dom.getElement('transaction-form');
  formEl.submit();
};


/**
 * @param {goog.events.Event} e The event for the submit button.
 * @private
 */
elevate300.Transaction.prototype.deleteButtonHandler_ = function(e) {
  
  // TODO:  Add an "Are you sure dialog box"
  
  
  var emailAddressEl = goog.dom.getElement('email-address');
  emailAddressEl.disabled = true;
  // The challengeType will determine the redirect location so not disabled.
  var amountEl = goog.dom.getElement('amount');
  amountEl.disabled = true;
  var casinoSelectEl = goog.dom.getElement('casino-select');
  casinoSelectEl.disabled = true;
  var casinoTextEl = goog.dom.getElement('casino-text');
  casinoTextEl.disabled = true;
  var gamePlayedSelectEl = goog.dom.getElement('game-played-select');
  gamePlayedSelectEl.disabled = true;
  var gamePlayedTextEl = goog.dom.getElement('game-played-text');
  gamePlayedTextEl.disabled = true;
  var notesEl = goog.dom.getElement('notes');
  notesEl.disabled = true;
  
  this.logger.info("Clicked delete");
  var deleteEl = goog.dom.getElement('is-delete');
  deleteEl.disabled = false;
  deleteEl.value = 'True';
  var formEl = goog.dom.getElement('transaction-form');
  formEl.submit();
};



/**
 * Event handler called when the email address select element changes.
 * @param {goog.events.Event} e
 * @private
 */
elevate300.Transaction.prototype.emailAddressChanged_ = function(e) {
  this.updateAddOnVisibility_();
};

/**
 * Event handler called when the challenge type select element changes.
 * @param {goog.events.Event} e
 * @private
 */
elevate300.Transaction.prototype.challengeTypeChanged_ = function(e) {
  this.updateAddOnVisibility_();
};


/**
 * Makes the Use add on button hidden if it is not applicable.
 * @private
 */
elevate300.Transaction.prototype.updateAddOnVisibility_ = function() {
  
  // Only called when the extra button is an Add On button
  var addOnButtonEl = goog.dom.getElement('extra-button');
  var emailAddressSelect = goog.dom.getElement('email-address');
  var emailAddressSelectIndex = emailAddressSelect.options.selectedIndex;
  var emailAddress = emailAddressSelect.options[emailAddressSelectIndex].value;    
  var challengeTypeSelect = goog.dom.getElement('challenge-type');
  var challengeTypeSelectIndex = challengeTypeSelect.options.selectedIndex;
  var challengeType = challengeTypeSelect.options[challengeTypeSelectIndex].value;
//  this.logger.info("email = " + emailAddress);
//  this.logger.info("challenge type = " + challengeType);

  var visibilityStr = 'visible';
  if (challengeType == '2') {
    visibilityStr = 'hidden';
  } else {
    for (var i = 0; i < this.addOnsUsed.length; i++) {
      var addOnUsed = this.addOnsUsed[i];
//      this.logger.info("Add on email = " + addOnUsed['email_address']);
//      this.logger.info("Add on challenge type = " + addOnUsed['challenge_type']);
      if (emailAddress == addOnUsed['email_address'] &&
          challengeType == addOnUsed['challenge_type']) {
          visibilityStr = 'hidden';
          break;
      }
    }    
  }
//  var submitEl = goog.dom.getElement('submit');
//  if (visibilityStr == 'hidden') {
//    goog.style.setStyle(submitEl, 'margin-top', '0');
//    goog.style.setStyle(submitEl, 'height', '30px');
//    goog.style.setStyle(submitEl, 'padding-top', '0');
//  } else {
//    goog.style.setStyle(submitEl, 'margin-top', '5px');
//    goog.style.setStyle(submitEl, 'height', '50px');
//    goog.style.setStyle(submitEl, 'padding-top', '15px');
//  }
  goog.style.setStyle(addOnButtonEl, 'visibility', visibilityStr);
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
	var textLabels = goog.dom.getElementsByClass('text-input-label');
	for (var i = 0; i < textLabels.length; i++) {
		goog.style.setStyle(textLabels[i], 'width', textLabelWidth + 'px');
	}
	var textBoxWidth = formWidth - textLabelWidth - 14;
  var textBoxes = goog.dom.getElementsByClass('text-input-box');
	for (var i = 0; i < textBoxes.length; i++) {
		goog.style.setStyle(textBoxes[i], 'width', textBoxWidth + 'px');
	}
	var gamePlayedSelect = goog.dom.getElement('game-played-select');
	goog.style.setStyle(gamePlayedSelect, 'width', textBoxWidth + 'px');
  var casinoSelect = goog.dom.getElement('casino-select');
  goog.style.setStyle(casinoSelect, 'width', textBoxWidth + 'px');
  
  // Manually center the extra button
  // Like most items in this area this task should really be done via CSS,
  // but I suck at CSS and JavaScript is so easy and makes sense.
  var extraButtonWidth = 120;
  var extraButtonLeft = (screenWidth - extraButtonWidth) / 2;
  var extraButtonEl = goog.dom.getElement('extra-button');
  goog.style.setStyle(extraButtonEl, 'width', extraButtonWidth + 'px');
  goog.style.setStyle(extraButtonEl, 'left', extraButtonLeft + 'px');
};
