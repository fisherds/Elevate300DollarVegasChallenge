#!/usr/bin/env python
# fisherds@gmail.com (Dave Fisher)

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
import model
	
class LeaderboardHandler(webapp.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/html'
		gamblingTransactions = db.GqlQuery('SELECT * FROM GamblingTransaction ORDER BY when DESC')
		values = {'gamblingTransactions': gamblingTransactions}
		
		# Do some data manipulations
		
		self.response.out.write(template.render('leaderboard.html', values))

def main():
	application = webapp.WSGIApplication([('/leaderboard', LeaderboardHandler)], debug=True)
	util.run_wsgi_app(application)

if __name__ == '__main__':
	main()
