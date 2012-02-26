#!/usr/bin/env python
# fisherds@gmail.com (Dave Fisher)

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
import datetime
import model

class EntryHandler(webapp.RequestHandler):
	def get(self):
		time = datetime.datetime.now()
		self.response.headers['Content-Type'] = 'text/html'
		gamblingTransactions = db.GqlQuery('SELECT * FROM GamblingTransaction ORDER BY when DESC')
		values = {'gamblingTransactions': gamblingTransactions}
		self.response.out.write(template.render('entry.html', values))
	def post(self):
		try:
			gamblingTransaction = model.GamblingTransaction(
				name=self.request.get('name'),
				challengeType=int(self.request.get('challengeType')),
				amount=float(self.request.get('amount')),
				casino=self.request.get('casino'),
				gamePlayed=self.request.get('gamePlayed'),
				comment=self.request.get('comment'))
			gamblingTransaction.put();
		except ValueError:
			# User entered a value that wasn't legal.  Ignore for now.
			pass
		self.redirect('/entry')

def main():
	application = webapp.WSGIApplication([('/entry', EntryHandler)], debug=True)
	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()
