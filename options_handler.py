#!/usr/bin/env python
# fisherds@gmail.com (Dave Fisher)

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
import userprefs
import member
import trip
import logging
	
class OptionsHandler(webapp.RequestHandler):
	
	def get(self):
		self.response.headers['Content-Type'] = 'text/html'
		user = users.get_current_user()
		currentTrip = userprefs.get_users_current_trip()
		allMyTrips = member.get_all_trips_for_email(user.email())
		tripFields = []
		for trip in allMyTrips:
			if trip.key().id() == currentTrip.key().id():
				continue # Don't add the current trip to this list
			tripField = {'tripName': trip.trip_name, 'tripKeyId': trip.key().id()}
			tripFields.append(tripField)
		values = {'tripFields': tripFields, 'currentTripName': currentTrip.trip_name, 'currentTripKeyId': currentTrip.key().id()}
		self.response.out.write(template.render('templates/options.html', values))

	# The only post to the options page is to change the current trip
	# The post will have a parameter for 'current-trip-select'
	def post(self):
		userPreference = userprefs.get_userprefs()
		logging.info(self.request)
		try:
			idSelected = self.request.get('current-trip-select')
			if idSelected != 0:
				newCurrentTrip = trip.get_trip(int(idSelected))
				userPreference.current_trip = newCurrentTrip
				userPreference.put()
		except:
			# User entered a value that wasn't legal.  Ignore for now.
			logging.info("Trip not set")
		self.redirect('/options')

def main():
	application = webapp.WSGIApplication([('/options', OptionsHandler)], debug=True)
	util.run_wsgi_app(application)

if __name__ == '__main__':
	main()
