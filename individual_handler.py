#!/usr/bin/env python
# fisherds@gmail.com (Dave Fisher)

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
import logging
import userprefs
import transaction
import member
	
class IndividualHandler(webapp.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/html'
		playerResults = {}
		currentTrip = userprefs.get_users_current_trip()
		allTransactions = currentTrip.get_all_transactions()
		for aTransaction in allTransactions:
			# Building up a dictionary of playerResults using the email as the key in a dictionary
			key = aTransaction.email_address
			if not key in playerResults:
				# This is a new entry in the playerResult dictionary fill in from scratch
				playerResult = {}
				playerResult['total'] = 0
				thisMember = member.get_member_for_trip(currentTrip.key(), aTransaction.email_address);
				playerResult['name'] = thisMember.display_name
				playerResult['email'] = thisMember.email_address
				playerResult['gamblingEvents'] = []
			else:
				playerResult = playerResults[key]

			# Add this transaction to the gamblingEvents
			gamblingEvent = {}
			gamblingEvent['challengeType'] = ''
			if aTransaction.challenge_type == transaction.CHALLENGE_TYPE_300_DOLLAR_CHALLENGE:
				gamblingEvent['challengeType'] = '$300 Challenge'
			elif aTransaction.challenge_type == transaction.CHALLENGE_TYPE_SECOND_CHANCE:
				gamblingEvent['challengeType'] = '2nd Chance'
			elif aTransaction.challenge_type == transaction.CHALLENGE_TYPE_INDIVIDUAL_ONLY:
				gamblingEvent['challengeType'] = 'Individual only'
			
			if (aTransaction.amount < 0):
				amountStr = "-$%0.2f" % + abs(aTransaction.amount)
			else:
				amountStr = "+$%0.2f" % aTransaction.amount
			gamblingEvent['amountStr'] = amountStr.replace('.00', '')  # Remove trailing zeros if integer	
			gamblingEvent['amount'] = aTransaction.amount
			gamblingEvent['casino'] = aTransaction.casino
			gamblingEvent['gamePlayed'] = aTransaction.game_played
			gamblingEvent['notes'] = aTransaction.notes
			gamblingEvent['id'] = aTransaction.key().id()
			
			playerResult['gamblingEvents'].append(gamblingEvent)
			playerResult['total'] = playerResult['total'] + aTransaction.amount
			playerResults[key] = playerResult
		
		# Okay at this point all of the transactions have been organized into the playerResults dictionary the structure is like this
		# {'fisherds@gmail.com':
		#    {'total': 15.5,
		#     'name': 'Dave',
		#     'gamblingEvents': [{'id': 1, 'amount': 10.0, 'casino': 'Luxor', 'gamePlayed': 'Blackjack',     'notes': 'blah blah', 'id': 432},
		#                        {'id': 3, 'amount':  5.5, 'casino': 'MGM',   'gamePlayed': "Texas Hold'em", 'notes': 'blah blah', 'id': 511}, ... ]},
		#   ... }		
		
		# Order the keys by amount and create the necessary strings
		allKeys = playerResults.keys()
		sortedKeys = sorted(allKeys, key=lambda resultKey: -playerResults[resultKey]['total'])
		displayResults = []
		for aKey in sortedKeys:
			displayResult = {}
			displayResult['name'] = playerResults[aKey]['name']
			displayResult['id'] = playerResults[aKey]['email']
			displayResult['total'] = playerResults[aKey]['total']
			if (playerResults[aKey]['total'] < 0):
				totalStr = "-$%0.2f" % + abs(playerResults[aKey]['total'])
			else:
				totalStr = "+$%0.2f" % playerResults[aKey]['total']
			displayResult['totalStr'] = totalStr.replace('.00', '')  # Remove trailing zeros if integer
			displayResult['gamblingEvents'] = playerResults[aKey]['gamblingEvents']
			displayResults.append(displayResult)

		logging.info(playerResults)
		logging.info(displayResults)
		values = {'displayResults': displayResults}
		self.response.out.write(template.render('templates/individual.html', values))

def main():
	application = webapp.WSGIApplication([('/individual', IndividualHandler)], debug=True)
	util.run_wsgi_app(application)

if __name__ == '__main__':
	main()
