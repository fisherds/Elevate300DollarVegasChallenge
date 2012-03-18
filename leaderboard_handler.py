#!/usr/bin/env python
# fisherds@gmail.com (Dave Fisher)

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
import userprefs
import transaction
import member
import logging
	
class LeaderboardHandler(webapp.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/html'
		playerResults = {}
		currentTrip = userprefs.get_users_current_trip()
		allTransactions = currentTrip.get_all_transactions()
		for aTransaction in allTransactions:
			if aTransaction.challenge_type == transaction.CHALLENGE_TYPE_INDIVIDUAL_ONLY:
				continue # Skip individual only for this page.
			# Building up a dictionary of playerResults using the email and challenge type as the key in a dictionary
			key = aTransaction.email_address + str(aTransaction.challenge_type)
			if not key in playerResults:
				# This is a new entry in the playerResult dictionary fill in from scratch
				playerResult = {}
				playerResult['total'] = 150
				thisMember = member.get_member_for_trip(currentTrip.key(), aTransaction.email_address);
				playerResult['name'] = thisMember.display_name
				playerResult['challengeType'] = aTransaction.challenge_type
				playerResult['gamblingEvents'] = []
			else:
				playerResult = playerResults[key]
			
			# Each playerResult has a list of gamblingEvents, add this transaction to the gamblingEvents list
			gamblingEvent = {}
			if (aTransaction.amount < 0):
				amountStr = "-$%0.2f" % + abs(aTransaction.amount)
			else:
				amountStr = "+$%0.2f" % aTransaction.amount
			gamblingEvent['amount'] = amountStr
			gamblingEvent['casino'] = aTransaction.casino
			gamblingEvent['gamePlayed'] = aTransaction.game_played
			gamblingEvent['notes'] = aTransaction.notes
			gamblingEvent['id'] = aTransaction.key().id()
			playerResult['gamblingEvents'].append(gamblingEvent)
			
			playerResult['total'] = playerResult['total'] + aTransaction.amount
			if playerResult['total'] > 300:
				playerResult['total'] = 300
			if playerResult['total'] < 0:
				playerResult['total'] = 0
			
			playerResults[key] = playerResult
		
		# Okay at this point all of the transactions have been organized into the playerResults dictionary the structure is like this
		# {'fisherds@gmail.com1':
		#    {'total': 165.5,
		#     'name': 'Dave',
		#     'challengeType': 1,
		#     'gamblingEvents': [{'amount': 10.0, 'casino': 'Luxor', 'gamePlayed': 'Blackjack',     'notes': 'blah blah', 'id': 432},
		#                        {'amount':  5.5, 'casino': 'MGM',   'gamePlayed': "Texas Hold'em", 'notes': 'blah blah', 'id': 511}, ... ]},
		#   ... }
		
		# TODO: Next we need to lookup and add the Add-Ons
		#   Change the total and add a field to the dictionary
		# {'fisherds@gmail.com1':
		#    {'total': 215.5,
		#     'name': 'Dave',
		#     'challengeType': 1,
		#     'usedAddOn': True,
		#     'gamblingEvents': [{'amount': 10.0, 'casino': 'Luxor', 'gamePlayed': 'Blackjack',     'notes': 'blah blah', 'id': 432},
		#                        {'amount':  5.5, 'casino': 'MGM',   'gamePlayed': "Texas Hold'em", 'notes': 'blah blah', 'id': 511}, ... ]},
		#   ... }
		
		# Order the keys by their total and create the necessary strings for the renderer
		allKeys = playerResults.keys()
		logging.info(allKeys)
		# sort the keys using the total
		sortedKeys = sorted(allKeys, key=lambda resultKey: -playerResults[resultKey]['total'])
		logging.info(sortedKeys)		
		displayResults = []
		for aKey in sortedKeys:
			displayResult = {}
			displayResult['challengeId'] = playerResults[aKey]['name'] + '_type_' + str(playerResults[aKey]['challengeType'])
			# Prepare the text that will be displayed at the top level
			challengeText = ''
			if playerResults[aKey]['challengeType'] == transaction.CHALLENGE_TYPE_PRACTICE:
				challengeText = ' Practice'
			elif playerResults[aKey]['challengeType'] == transaction.CHALLENGE_TYPE_SECOND_CHANCE:
				challengeText = ' 2nd Chance'
			addOnText = ''
			if hasattr(playerResults[aKey], 'userAddOn') and playerResults[aKey]['usedAddOn']:
				addOnText = '*'
			displayResult['challengeDescription'] = playerResults[aKey]['name'] + addOnText + challengeText
			if (playerResults[aKey]['total'] < 0):
				amountStr = "-$%0.2f" % + abs(playerResults[aKey]['total'])
			else:
				amountStr = "$%0.2f" % playerResults[aKey]['total']
			displayResult['amountStr'] = amountStr
			displayResult['gamblingEvents'] = playerResults[aKey]['gamblingEvents']
			displayResults.append(displayResult)

		#names.append(aTransaction.name)
		logging.info(playerResults)
		logging.info(displayResults)
		values = {'displayResults': displayResults}
		self.response.out.write(template.render('templates/leaderboard.html', values))

def main():
	application = webapp.WSGIApplication([('/leaderboard', LeaderboardHandler)], debug=True)
	util.run_wsgi_app(application)

if __name__ == '__main__':
	main()
