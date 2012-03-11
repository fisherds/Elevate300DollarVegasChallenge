#!/usr/bin/env python
# fisherds@gmail.com (Dave Fisher)

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
import model
import logging
	
class LeaderboardHandler(webapp.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/html'
		userprefs = model.get_userprefs()
		query = db.Query(model.GamblingTransaction)
		query.ancestor(userprefs.currentTrip)
		query.order('-when')
		
		# Organize the transactions based on player and game type
		playerResults = {}
		for transaction in query:
			if transaction.challengeType == 3:
				continue
			key = transaction.emailAddress + str(transaction.challengeType)
			if not key in playerResults:
				# This is a new entry in the playerResult fill in from scratch
				playerResult = {}
				playerResult['total'] = 150
				playerResult['name'] = transaction.emailAddress
				playerResult['challengeType'] = transaction.challengeType
				playerResult['gamblingEvents'] = []
			else:
				playerResult = playerResults[key]
			
			# Add this transaction to the gamblingEvents
			gamblingEvent = {}
			
			if (transaction.amount < 0):
				amountStr = "-$%0.2f" % + abs(transaction.amount)
			else:
				amountStr = "+$%0.2f" % transaction.amount
			gamblingEvent['amount'] = amountStr
			gamblingEvent['casino'] = transaction.casino
			gamblingEvent['gamePlayed'] = transaction.gamePlayed
			gamblingEvent['notes'] = transaction.notes
			gamblingEvent['key_name'] = transaction.key().name()
			
			playerResult['gamblingEvents'].append(gamblingEvent)
			playerResult['total'] = playerResult['total'] + transaction.amount
			if playerResult['total'] > 300:
				playerResult['total'] = 300
			if playerResult['total'] < 0:
				playerResult['total'] = 0
			playerResults[key] = playerResult
		
		
		# Order the keys by amount and create the necessary strings
		allKeys = playerResults.keys()
		# sort the keys using the total
		displayResults = []
		for aKey in allKeys:
			displayResult = {}
			displayResult['challengeDescription'] = playerResults[aKey]['name'] + '_type_' + str(playerResults[aKey]['challengeType'])
			if (playerResults[aKey]['total'] < 0):
				amountStr = "-$%0.2f" % + abs(playerResults[aKey]['total'])
			else:
				amountStr = "$%0.2f" % playerResults[aKey]['total']
			displayResult['amountStr'] = amountStr
			displayResult['gamblingEvents'] = playerResults[aKey]['gamblingEvents']
			displayResults.append(displayResult)
		
		#transaction.name = db.StringProperty(default='')
		#transaction.challengeType = db.IntegerProperty(default=3)
		#transaction.amount = db.FloatProperty(default=0)
		#transaction.casino = db.StringProperty(default='')
		#transaction.gamePlayed = db.StringProperty(default='')
		#transaction.notes = db.StringProperty(default='')
		#transaction.when = db.DateTimeProperty(auto_now_add=True)
			
		#names.append(transaction.name)
		logging.info(playerResults)
		logging.info(displayResults)
		values = {'displayResults': displayResults}
		self.response.out.write(template.render('templates/leaderboard.html', values))

def main():
	application = webapp.WSGIApplication([('/leaderboard', LeaderboardHandler)], debug=True)
	util.run_wsgi_app(application)

if __name__ == '__main__':
	main()
