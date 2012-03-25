#!/usr/bin/env python
# fisherds@gmail.com (Dave Fisher)

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings' 
from google.appengine.dist import use_library
use_library('django', '1.2')
from django.conf import settings
_ = settings.TEMPLATE_DIRS

import datetime
import member
import transaction
import userprefs
import logging

class TransactionHandler(webapp.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/html'
		currentTrip = userprefs.get_users_current_trip()
		user = users.get_current_user()
		currentMember = member.get_member_for_trip(currentTrip.key(), user.email())
		select_email = member.standardize_email_address(user.email())
		amountValue = ''
		select_challenge_type = 0
		selectCasino = ''
		selectGamePlayed = ''
		transaction_id = 0
		
		# Hardcode some casinos to practice with the JS
		# These are passed into the JavaScript then JS fills in the casino options
		# This list can get very large.
		mtv = {'name': 'Fisher apt', 'latitude': 37.3958471, 'longitude': -122.0937461}
		mgm = {'name': 'MGM Grand', 'latitude': 1, 'longitude': 4}
		mandalayBay = {'name': 'Mandalay Bay', 'latitude': 12, 'longitude': 45}
		luxor = {'name': 'Luxor', 'latitude': 123, 'longitude': 456}
		casinoOptions = [mtv, mgm, mandalayBay, luxor]
		
		# Hardcode some games to practice with the JS
		# These are used by Django
		gamePlayedOptions = ['Blackjack', "Hold'em (no limit)", "Hold'em (limit)","Hold'em (tournament)",
			'Roulette', 'Craps', 'Slots', 'Pai gow poker']
		
		# Hardcode add ons used to practice with the JS
		# These are passed into the JavaScript
		addOn1 = {'email_address': 'test@example.com', 'challenge_type': '0'}
		addOn2 = {'email_address': 'test42@example.com', 'challenge_type': '1'}
		addOnsUsed = [addOn1, addOn2]
		
		editingTransactionId = self.request.get('id')
		if editingTransactionId and int(editingTransactionId) != 0: # Shouldn't ever send 0, but just in case my other code glitches :)
			# Get the transaction with this id
			transaction_id = int(editingTransactionId)
			editingTransaction = transaction.get_trip_transaction(currentTrip.key(), transaction_id)
			notes = editingTransaction.notes
			select_email = editingTransaction.email_address
			amountValue = str(editingTransaction.amount)
			select_challenge_type = editingTransaction.challenge_type
			selectCasino = editingTransaction.casino
			selectGamePlayed = editingTransaction.game_played
		else:
			time = datetime.datetime.now()
			now = datetime.datetime.now()
			now += datetime.timedelta(0, 0, 0, 0, 0, -7);  # TODO: Handle daylight savings time issue (-8 standard)
			# for attr in [ 'year', 'month', 'day', 'hour', 'minute', 'second', 'microsecond']:
			#     print attr, ':', getattr(now, attr)
			# format = "%a %b %d %Y at %H:%M"
			format = "%a"
			dayString = now.strftime(format)
			# notes = 'Created by ' + currentMember.display_name + ' on ' + dateString
			dateString = str(now.month) + "/" + str(now.day) + "/" + str(now.year)
			if now.hour == 0:
				hourStr = '12'
				amPm = 'am'
			elif now.hour < 12:
				hourStr = str(now.hour)
				amPm = 'am'
			elif now.hour == 12:
				hourStr = str(now.hour)
				amPm = 'pm'
			else:
				hourStr = str(now.hour - 12)
				amPm = 'pm'
			timeString =  "%s:%02d %s" % (hourStr, now.minute, amPm)
			notes = 'Created by ' + currentMember.display_name + ' on ' + dayString + ' ' + dateString + ' at ' + timeString
			# DateTime docs at http://docs.python.org/library/datetime.html
		
		
		values = {'transaction_id': transaction_id,
				  'trip_member_options': currentTrip.get_all_members(),
				  'select_email': select_email,
				  'challenge_type_options': transaction.CHALLENGE_TYPES,
				  'select_challenge_type': select_challenge_type,
				  'amount_value': amountValue,
				  'casino_options': casinoOptions,
				  'select_casino': selectCasino,
				  'game_played_options': gamePlayedOptions,
				  'select_game_played': selectGamePlayed,
				  'notes': notes,
				  'add_ons_used': addOnsUsed}
		self.response.out.write(template.render('templates/transaction.html', values))

	def post(self):
		logging.info(self.request)
		currentTrip = userprefs.get_users_current_trip()
		if self.request.get('is_delete') == 'True':
			try:
				currentTrip.delete_transaction(int(self.request.get('transaction_id')))
			except:
				logging.warning("Error: Exception occurred and transaction was not deleted.")
		elif self.request.get('is_add_on') == 'True':
			try:
				email_address = self.request.get('email_address')
				currentTrip.create_add_on(email_address = self.request.get('email_address'),
					challenge_type = int(self.request.get('challenge_type')),
					used_add_on=True)
			except:
				logging.warning("Error: Exception occurred and add on was not added.")
		else:
			try:
				gamePlayed = self.request.get('game_played_select')
				if not gamePlayed or len(gamePlayed) == 0 or gamePlayed == "Other":
					gamePlayed = self.request.get('game_played_text')
				if len(gamePlayed) == 0:
					gamePlayed = 'No game listed'
			 	casino = self.request.get('casino_select')
				if not casino or len(casino) == 0 or casino == "Other":
					casino = self.request.get('casino_text')
				if len(casino) == 0:
					casino = 'No casino'
				amount = self.request.get('amount')
				if len(amount) == 0:
					amount = 0
				# logging.info(self.request.get('email_address'))	
				# logging.info(str(int(self.request.get('challenge_type'))))
				# logging.info(self.request.get('amount'))	
				# logging.info(self.request.get('casino'))
				# logging.info(gamePlayed)
				# logging.info(self.request.get('notes'))
				editingTransactionId = self.request.get('transaction_id')
				if editingTransactionId and int(editingTransactionId) != 0: # Shouldn't ever send 0, but just in case my other code glitches :)
					currentTrip.update_transaction(transaction_id = int(editingTransactionId),
						email_address = self.request.get('email_address'),
						challenge_type = int(self.request.get('challenge_type')),
						amount = float(amount),
						casino = casino,
						game_played = gamePlayed,
						notes = self.request.get('notes'))				
				else: 
					currentTrip.create_transaction(email_address = self.request.get('email_address'),
						challenge_type = int(self.request.get('challenge_type')),
						amount = float(amount),
						casino = casino,
						game_played = gamePlayed,
						notes = self.request.get('notes'))
			except:
				logging.warning("Error: Exception occurred and transaction was not added.")
		
		if int(self.request.get('challenge_type')) == transaction.CHALLENGE_TYPE_INDIVIDUAL_ONLY:
			self.redirect('/individual')
		else:
			self.redirect('/leaderboard')

def main():
	application = webapp.WSGIApplication([('/transaction', TransactionHandler)], debug=True)
	util.run_wsgi_app(application)

if __name__ == '__main__':
	main()
