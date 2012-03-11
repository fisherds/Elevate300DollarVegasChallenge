#!/usr/bin/env python
# fisherds@gmail.com (Dave Fisher)

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
import datetime
import model

class TransactionHandler(webapp.RequestHandler):
	def get(self):
		time = datetime.datetime.now()
		self.response.headers['Content-Type'] = 'text/html'
		#gamblingTransactions = db.GqlQuery('SELECT * FROM GamblingTransaction ORDER BY when DESC')
		
		userprefs = model.get_userprefs()
		query = db.Query(model.GamblingTransaction)
		query.ancestor(userprefs.currentTrip)
		query.order('-when')
		gamblingTransactions = query.fetch(limit=100)
		values = {'gamblingTransactions': gamblingTransactions}
		self.response.out.write(template.render('templates/transaction.html', values))
	def post(self):
		userprefs = model.get_userprefs()
		try:
			gamblingTransaction = model.GamblingTransaction(
				parent = userprefs.currentTrip,
				emailAddress=self.request.get('emailAddress'),
				challengeType=int(self.request.get('challengeType')),
				amount=float(self.request.get('amount')),
				casino=self.request.get('casino'),
				gamePlayed=self.request.get('gamePlayed'),
				notes=self.request.get('notes'))
			gamblingTransaction.put();
		except ValueError:
			# User entered a value that wasn't legal.  Ignore for now.
			pass
		self.redirect('/transaction')

def main():
	application = webapp.WSGIApplication([('/transaction', TransactionHandler)], debug=True)
	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()
