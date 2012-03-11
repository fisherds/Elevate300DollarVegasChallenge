#!/usr/bin/env python
# fisherds@gmail.com (Dave Fisher)

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
import model
import logging
	
class OptionsHandler(webapp.RequestHandler):
	def post(self):
		userprefs = model.get_userprefs()
		try:
			idSelected = self.request.get('current-trip-select')
			logging.info("Selected key = " + idSelected)
			key = db.Key.from_path('Trip', int(idSelected))
			userprefs.currentTrip = key
			userprefs.put()
		except:
			# User entered a value that wasn't legal.  Ignore for now.
			logging.info("Trip not set")
		self.redirect('/options')
	def get(self):
		self.response.headers['Content-Type'] = 'text/html'
		user = users.get_current_user()
		userprefs = model.get_userprefs()
		currentTrip = model.get_current_trip()
		query = db.Query(model.TripMember)
		query.filter("emailAddress =", userprefs.user.email().lower())
		query.order('-when')
		tripFields = []
		for tripMember in query:
			trip = tripMember.parent()
			if trip.key().id() == currentTrip.key().id():
				continue # Don't add the current trip to this list
			logging.info("trip name = " + trip.name)
			logging.info("trip key id = " + str(trip.key().id()))
			logging.info("trip member email = " + tripMember.emailAddress)
			logging.info("trip member name = " + tripMember.displayName)
			tripField = {'tripName': trip.name, 'tripKeyId': trip.key().id()}
			tripFields.append(tripField)
		values = {'tripFields': tripFields, 'currentTripName': currentTrip.name, 'currentTripKeyId': currentTrip.key().id()}
		self.response.out.write(template.render('templates/options.html', values))
		
def main():
	application = webapp.WSGIApplication([('/options', OptionsHandler)], debug=True)
	util.run_wsgi_app(application)

if __name__ == '__main__':
	main()
