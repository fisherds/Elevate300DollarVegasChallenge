#!/usr/bin/env python
# Model object module with all the data storage classes and helper functions.
# fisherds@gmail.com (Dave Fisher)

from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext import db
import logging
import trip
import re

# Holds the meta data representing a single person on a trip.
#   Entities will be children of a Trip entity.
# The key_name for entities will be the standardized email address.
# Note that the trip parent will make Members unique.
class Member(db.Model):
	email_address = db.StringProperty(required=True) # TODO: Figure out how to remove since it is the key_name now
	display_name = db.StringProperty(default='')
	phone_number = db.StringProperty(default='')
	created_date_time = db.DateTimeProperty(auto_now_add=True)
	
	def cache_set(self):
		logging.info("Memcache: Set " + str(self.key().kind()) + " with key " + "trip_id:" + str(self.parent().key().id()) + "key_name:" + self.key().name())
		memcache.set("trip_id:" + str(self.parent().key().id()) + "key_name:" + self.key().name(), self, namespace=self.key().kind())

	def cache_delete(self):
		logging.info("Memcache: Delete " + str(self.key().kind()) + " with key " + "trip_id:" + str(self.parent().key().id()) + "key_name:" + self.key().name())
		memcache.delete("trip_id:" + str(self.parent().key().id()) + "key_name:" + self.key().name(), namespace=self.key().kind())

	def put(self):
		db.Model.put(self)
		self.cache_set()
		
	def delete(self):
		db.Model.delete(self)
		self.cache_delete()
		

# Gets Member data when you know the trip id and the email address
# Will create a new member if none exists.
# Does NOT push the member into the data store (unless it is just created now).
def get_member_for_trip(trip_key, email_address):
	standardized_email_address = standardize_email_address(email_address)
	tripMember = memcache.get("trip_id:" + str(trip_key.id()) + "key_name:" + standardized_email_address, namespace='Member')
	if tripMember:
		logging.info('Memcache: Retrieved Member for ' + "trip_id:" + str(trip_key.id()) + "key_name:" + standardized_email_address)
	if not tripMember:
		key = db.Key.from_path('Trip', trip_key.id(), 'Member', standardized_email_address)
		tripMember = db.get(key)
		if tripMember:
			logging.info('Datastore: Retrieved Member for ' + "trip_id:" + str(trip_key.id()) + "key_name:" + standardized_email_address)
			tripMember.cache_set()
		else:
			# Consider: I'm not sure that creating a new member is the way to do this!!!
			# Consider: Changing this to returning null and then check for side effects.
			#
			# Let me explain what happen in this bug here instead of issue tracker (because I'm on a plane)
			#
			# I added golfer@gmail.com and added a transaction for him.
			# Then Scott deleted golfer@gmail.com and added mholzie@gmail.com
			# This left an orphan transaction for the email address golfer@gmail.com
			# The leaderboard_handler then got the display name for golfer@gmail.com for that transaction
			# Scott was the person logged in at the time.
			# When this code ran it 
			
			logging.info('New: Created Member for ' + "trip_id:" + str(trip_key.id()) + "key_name:" + standardized_email_address)
			tripEntity = trip.get_trip(trip_key.id())
			tripMember = tripEntity.create_member(standardized_email_address)
	return tripMember	

# Returns all the trips for this email address.
def get_all_trips_for_email(email_address):
	standardized_email_address = standardize_email_address(email_address)
	# I'm choosing not to memcache this result as the query is not common.
	query = db.Query(Member)
	query.filter("email_address =", standardized_email_address)
	query.order('-created_date_time')
	allTrips = []
	for aTrip in query:
		allTrips.append(aTrip.parent())
	return allTrips

# gmail allows only letters (a-z), numbers, and periods(which it then ignores).
def standardize_email_address(original_email_address):
	if len(original_email_address) == 0:
		return ''
	# Always use lower case and trim trailing whitespace
	email = original_email_address.strip().lower()
	emailComponents = email.split('@')
	username = emailComponents[0].replace('.', '')  # remove periods
	# If a domain was NOT given assume it is a gmail.com account
	if len(emailComponents) < 2:
		domain = 'gmail.com'
	else:
		domain = emailComponents[1]
	return username + '@' + domain


# A phone number is string 10 characters long where each character is a digit
def standardize_phone_number(original_phone_number):
	newPhoneNumber = re.sub(r"\D", "", original_phone_number)
	if len(newPhoneNumber) != 10:
		newPhoneNumber = ''
	return newPhoneNumber
