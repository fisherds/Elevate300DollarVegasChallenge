#!/usr/bin/env python
# fisherds@gmail.com (Dave Fisher)

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
import model
import logging
	
class IndividualHandler(webapp.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/html'
		#gamblingTransactions = db.GqlQuery('SELECT * FROM GamblingTransaction ORDER BY when DESC')
		userprefs = model.get_userprefs()
		query = db.Query(model.GamblingTransaction)
		query.ancestor(model.get_current_trip())
		query.order('-when')
		gamblingTransactions = query.fetch(limit=100)
		
		
		# Organize the transactions based on player and game type
		playerResults = {}
		for transaction in gamblingTransactions:
			key = transaction.emailAddress
			if not key in playerResults:
				# This is a new entry in the playerResult fill in from scratch
				playerResult = {}
				playerResult['total'] = 0
				playerResult['name'] = transaction.emailAddress
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
			playerResults[key] = playerResult
		
		
		# Order the keys by amount and create the necessary strings
		allKeys = playerResults.keys()
		# sort the keys using the total
		displayResults = []
		for aKey in allKeys:
			displayResult = {}
			displayResult['challengeDescription'] = playerResults[aKey]['name']
			if (playerResults[aKey]['total'] < 0):
				amountStr = "-$%0.2f" % + abs(playerResults[aKey]['total'])
			else:
				amountStr = "+$%0.2f" % playerResults[aKey]['total']
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
		self.response.out.write(template.render('templates/individual.html', values))

def main():
	application = webapp.WSGIApplication([('/individual', IndividualHandler)], debug=True)
	util.run_wsgi_app(application)

if __name__ == '__main__':
	main()
