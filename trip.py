#!/usr/bin/env python
# fisherds@gmail.com (Dave Fisher)

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
import model
	
class TripHandler(webapp.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/html'
		self.response.out.write(template.render('html/trip.html', {}))
		
	def post(self):
		self.redirect('/leaderboard')

def main():
	application = webapp.WSGIApplication([('/trip', TripHandler)], debug=True)
	util.run_wsgi_app(application)

if __name__ == '__main__':
	main()
