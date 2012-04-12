#!/usr/bin/env python
# fisherds@gmail.com (Dave Fisher)

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
import member
import trip
import userprefs
import logging
	
class TripHandler(webapp.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/html'
		user = users.get_current_user()
		# Set default values for the template data (that will be used if this is a new trip)
		creator_name = user.nickname()
		creator_email = member.standardize_email_address(user.email())
		creator_phone = ""
		trip_name = ""
		trip_key_id = 0
		trip_members = []
		can_delete = False
		# Determine if this is an edit or a new trip
		tripId = self.request.get('id')
		if tripId and int(tripId) != 0: # Shouldn't ever send 0, but just in case my other code glitches :)
			editTrip = trip.get_trip(int(tripId))
			if editTrip.is_a_member():
				# OK you are indeed in the requested trip id, you may edit.  Just checking.
				# Fill in fields with existing data
				trip_name = editTrip.trip_name
				trip_key_id = editTrip.key().id()
				can_delete = editTrip.created_by_user == user
				tripCreatorMember = member.get_member_for_trip(editTrip.key(), member.standardize_email_address(editTrip.created_by_user.email()))
				creator_name = tripCreatorMember.display_name
				creator_email = tripCreatorMember.email_address
				creator_phone = tripCreatorMember.phone_number
				
				
				allMembers = editTrip.get_all_members()
				for aMember in allMembers:
					if aMember.email_address != member.standardize_email_address(editTrip.created_by_user.email()):
						trip_members.append(aMember)
			else:
				self.response.out.write("You do not appear to have access to modify Trip id " + tripId)
				return

		values = {'creator_name': creator_name, 'creator_email': creator_email, 'creator_phone': creator_phone,
				  'trip_name': trip_name, 'trip_key_id': trip_key_id,
				  'trip_members': trip_members,
				  'can_delete': can_delete}
		self.response.out.write(template.render('templates/trip.html', values))
		
	def post(self):
		currentUserprefs = userprefs.get_userprefs()
		current_trip_name = self.request.get('trip_name')
		if len(current_trip_name) == 0:
			current_trip_name = 'Empty trip name'
		trip_key_id = int(self.request.get('trip_key_id', default_value=0))
		if trip_key_id != 0:
			current_trip = trip.get_trip(trip_key_id)
			current_trip.trip_name = current_trip_name
			current_trip.delete_non_creator_members()
		else:
			current_trip = trip.Trip(trip_name = current_trip_name)
		current_trip.put()
		currentUserprefs.current_trip = current_trip
		currentUserprefs.put()
		
		# Update the creator Member data
		creatorMember = member.get_member_for_trip(current_trip.key(), current_trip.created_by_user.email())
		creatorMember.display_name = self.request.get('creator_display_name')
		creatorMember.email_address = member.standardize_email_address(self.request.get('creator_email_address', default_value=''))
		creatorMember.phone_number = member.standardize_phone_number(self.request.get('creator_phone_number'))
		creatorMember.put()
		
		displayNameValues=self.request.get_all('display_name')
		emailAddressValues=self.request.get_all('email_address')
		phoneNumberValues=self.request.get_all('phone_number')
		for i in range(len(displayNameValues)):
			try:
				if len(emailAddressValues[i]) == 0:
					continue
				# Make the key name the email address
				standardized_email_address = member.standardize_email_address(emailAddressValues[i])
				newMember = member.get_member_for_trip(current_trip.key(), standardized_email_address)
				newMember.display_name = displayNameValues[i]
				newMember.email_address = standardized_email_address
				newMember.phone_number = member.standardize_phone_number(phoneNumberValues[i])
				newMember.put();
				# logging.info("Successfully added member.")
				# logging.info("i=" + str(i) + "  displayName = " + displayNameValues[i])
				# logging.info("i=" + str(i) + "  emailAddressValues = " + emailAddressValues[i].lower())
				# logging.info("i=" + str(i) + "  phoneNumberValues = " + phoneNumberValues[i])
			except:
				logging.info("Error: Did not add member at index " + str(i) + ".")
		
		
		# TODO: Clean up the transactions!!!!
		# If an email address got removed then the transactions for the deleted email must go!
		# That is one solution to this problem.
		
		self.redirect('/options')
  
def main():
	application = webapp.WSGIApplication([('/trip', TripHandler)], debug=True)
	util.run_wsgi_app(application)

if __name__ == '__main__':
	main()
