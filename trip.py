#!/usr/bin/env python
# fisherds@gmail.com (Dave Fisher)

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
import model
import logging
	
class TripHandler(webapp.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/html'
		user = users.get_current_user()
		# Set default values for the template data (that will be used if this is a new trip)
		creatorName = user.nickname()
		creatorEmail = user.email().lower()
		creatorPhone = ""
		tripName = ""
		tripKeyId = 0
		tripMembers = []
		canDelete = False
		# Determine if this is an edit or a new trip
		tripId = self.request.get('id')
		if tripId and int(tripId) != 0: # Shouldn't ever send 0, but just in case my other code glitches :)
			logging.info("Fill with the id " + tripId)
			tripKey = db.Key.from_path('Trip', int(tripId))
			trip = db.get(tripKey)  # TODO: use a get trip method to use memcache
			tripCreatorMember = model.get_trip_member(trip.key(), trip.creator.email().lower())
			creatorName = tripCreatorMember.displayName
			creatorEmail = tripCreatorMember.emailAddress
			creatorPhone = tripCreatorMember.phoneNumber
			# Make sure this email address is a member
			query = db.Query(model.TripMember)
			query.ancestor(trip.key())
			query.filter("emailAddress =", user.email().lower())
			aMember = query.get()
			#aMember = model.get_trip_member(trip.key(), user.email().lower())
			logging.info(aMember)
			if query.get():
				# OK you are indeed in the requested trip id, you may edit
				tripName = trip.name
				tripKeyId = trip.key().id()
				canDelete = trip.creator == user
				query = db.Query(model.TripMember) #TODO: Use memcache
				query.ancestor(trip.key())
				query.filter("emailAddress !=", trip.creator.email().lower()) # Don't include the creator in this list
				tripMembers = query.fetch(1000)  # Assumes not trip will have more than 1000 members
			else:
				self.response.out.write("You do not appear to have access to modify Trip id " + tripId)
				self.response.out.write("<br>Trip key " + str(trip.key()))
				self.response.out.write("<br>You are " + user.email().lower())
				tripMember = model.get_trip_member(trip.key(), user.email().lower())
				self.response.out.write("<br>You query found " + str(tripMember))
				self.response.out.write("<br>displayName " + tripMember.displayName)
				self.response.out.write("<br>emailAddress " + tripMember.emailAddress)
				self.response.out.write("<br>phoneNumber " + tripMember.phoneNumber)
				return
		else:
			logging.info("New trip")
		values = {'creatorName': creatorName,
							'creatorEmail': creatorEmail,
							'creatorPhone': creatorPhone,
							'tripName': tripName,
							'tripKeyId': tripKeyId,
							'tripMembers': tripMembers,
							'canDelete': canDelete}
		logging.info(values)
		self.response.out.write(template.render('templates/trip.html', values))
		
	def post(self):
		logging.info(self.request)
		userprefs = model.get_userprefs()
		tripName = self.request.get('tripName')
		if len(tripName) == 0:
			tripName = 'Empty trip name'
		tripKeyId = int(self.request.get('tripKeyId', default_value=0))
		if tripKeyId != 0:
			logging.info("Update to an existing trip")
			trip = model.get_trip(tripKeyId)
			trip.name = tripName
		else:
			logging.info("New trip")
			trip = model.Trip(name = tripName)
		trip.put()
		userprefs.currentTrip = trip.key()
		userprefs.put()
		
		displayNameValues=self.request.get_all('displayName')
		emailAddressValues=self.request.get_all('emailAddress')
		phoneNumberValues=self.request.get_all('phoneNumber')
		for i in range(len(displayNameValues)):
			try:
				# Make the key name the email address
				member = model.get_trip_member(trip.key(), emailAddressValues[i].lower())
				member.displayName=displayNameValues[i]
				member.emailAddress=emailAddressValues[i].lower()
				member.phoneNumber=phoneNumberValues[i]
				member.put();
				logging.info("Successfully added member.")
				logging.info("i=" + str(i) + "  displayName = " + displayNameValues[i])
				logging.info("i=" + str(i) + "  emailAddressValues = " + emailAddressValues[i].lower())
				logging.info("i=" + str(i) + "  phoneNumberValues = " + phoneNumberValues[i])
			except:
				logging.info("Did not add member at index " + str(i) + ".")
				
		self.redirect('/options')

  
def main():
	application = webapp.WSGIApplication([('/trip', TripHandler)], debug=True)
	util.run_wsgi_app(application)

if __name__ == '__main__':
	main()
