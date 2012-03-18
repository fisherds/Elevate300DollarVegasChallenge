#!/usr/bin/env python
# Model object module with all the data storage classes and helper functions.
# fisherds@gmail.com (Dave Fisher)

from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext import db
import logging
import trip
import member


# Entity that stores a users current trip.  This can be changed on the login
#   page, but only one trip can be active at a time.
# The key for entities will be the user_id of the Google account.  ALL access to
#   entity should be made via the get_userprefs method, no queries please.
class UserPrefs(db.Model):
	user = db.UserProperty(auto_current_user_add=True)
	current_trip = db.ReferenceProperty(trip.Trip, collection_name='current_trip_set')
	
	def cache_set(self):
		logging.info("Memcache: Set " + str(self.key().kind()) + " with key " + self.key().name())
		memcache.set(self.key().name(), self, namespace=self.key().kind())
		
	def put(self):
		self.cache_set()
		db.Model.put(self)


# Helper function to get the current user prefs.  Always use this helper.
def get_userprefs(user_id=None):
	if not user_id:
		user = users.get_current_user()
		if not user:
			return None
		user_id = user.user_id()
	userprefs = memcache.get(user_id, namespace='UserPrefs')
	if userprefs:
		logging.info('Memcache: Retrieved userprefs for user_id ' + user_id)
	else:
		key = db.Key.from_path('UserPrefs', user_id)
		userprefs = db.get(key)
		if userprefs:
			logging.info('Datastore: Retrieved userprefs for user_id ' + user_id)
			userprefs.cache_set()
		else:
			logging.info('New: Created userprefs for user_id ' + user_id)
			userprefs = UserPrefs(key_name=user_id)
	return userprefs


# Helper function to get the current trip.  Always use this helper.
def get_users_current_trip(user_id=None):
	userprefs = get_userprefs(user_id)
	if not userprefs.current_trip:
		_find_or_create_a_current_trip(userprefs)
		userprefs.put()
	return userprefs.current_trip
	# TODO: Figure out how to provide an opportunity to use the memcache (really really fast) instead of automatic dereferencing (really fast)
	#currentTrip = trip.get_trip(userprefs.current_trip.key().id())
	#return currentTrip


# Adds a trip to the user prefs.  Creates a trip if necessary.
def _find_or_create_a_current_trip(userprefs):
	standardized_email_address = member.standardize_email_address(userprefs.user.email())
	query = db.Query(member.Member)
	query.filter("email_address =", standardized_email_address)
	query.order("-created_date_time")
	mostRecentMemberEntityForEmail = query.get()
	if mostRecentMemberEntityForEmail:
		logging.info("Found a trip for email address " + standardized_email_address)
		userprefs.current_trip = mostRecentMemberEntityForEmail.key().parent()
	else:
		logging.info("Had to create a default trip for email address " + standardized_email_address)
		userprefs.current_trip = trip.create_default_trip()

