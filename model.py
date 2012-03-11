#!/usr/bin/env python
# fisherds@gmail.com (Dave Fisher)

from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext import db
import logging

# A Trip entity is the parent to TripMember and GamblingTransaction entities.
#   Generally a Trip entity should be accessed via the currentTrip reference
#   property of a UserPrefs.  Then the GamblingTransactions for the Trip can
#   be accessed because they are children of this entity.
# When finding all trips that an email address belongs to standard GQL queries
#   can be done via the TripMember children.
# The id for this group will be auto generated. A Trip is a root entity (no parent)
class Trip(db.Model):
  name = db.StringProperty(default='Default Trip')
  creator = db.UserProperty(auto_current_user_add=True)
  when = db.DateTimeProperty(auto_now_add=True)
  
  def cache_set(self):
		logging.info("Memcache: Set " + str(self.key().kind()) + " with key " + str(self.key().id()))
		memcache.set(str(self.key().id()), self, namespace=self.key().kind())
    
  def put(self):
		db.Model.put(self)
		self.cache_set()

# Entity that stores a single gambling transaction.  Each transaction is a
#   child of a trip entity.  The id for entities will be auto generated.
class GamblingTransaction(db.Model):
	emailAddress = db.StringProperty(required=True)
	challengeType = db.IntegerProperty(default=3)
	amount = db.FloatProperty(default=0)
	casino = db.StringProperty(default='')
	gamePlayed = db.StringProperty(default='')
	notes = db.StringProperty(default='')
	when = db.DateTimeProperty(auto_now_add=True)

# Holds the meta data representing a single person on a trip.
#   Entities will be children of a Trip entity.
#   The id for entities will be auto generated.
class TripMember(db.Model):
	emailAddress = db.StringProperty(required=True)
	displayName = db.StringProperty(default='')
	phoneNumber = db.StringProperty(default='')
	when = db.DateTimeProperty(auto_now_add=True)
	
	def cache_set(self):
		logging.info("Memcache: Set " + str(self.key().kind()) + " with key " + "trip:" + str(self.parent().key().id()) + "email:" + str(self.key().name()))
		memcache.set("trip:" + str(self.parent().key().id()) + "email:" + str(self.key().name()), self, namespace=self.key().kind())
	def put(self):
		db.Model.put(self)
		self.cache_set()

# Entity that stores a users current trip.  This can be changed on the login
#   page, but only one trip can be active at a time.
# The key for entities will be the user_id of the Google account.  ALL access to
#   entity should be made via the get_userprefs method, no queries please.
class UserPrefs(db.Model):
  user = db.UserProperty(auto_current_user_add=True)
  currentTrip = db.ReferenceProperty(Trip)
  
  def cache_set(self):
		logging.info("Memcache: Set " + str(self.key().kind()) + " with key " + self.key().name() + " for email " + self.user.email().lower())
		memcache.set(self.key().name(), self, namespace=self.key().kind())
  def put(self):
    self.cache_set()
    db.Model.put(self)

def get_trip(tripId=None):
	if not tripId:
		return None
	trip = memcache.get(str(tripId), namespace='Trip')
	if not trip:
		key = db.Key.from_path('Trip', tripId)
		trip = db.get(key)
		if trip:
			trip.cache_set()
		else:
			trip = Trip()
	return trip

# Helper function to get the current trip.  Always use this helper.
def get_current_trip(user_id=None):
	userprefs = get_userprefs(user_id)
	if not userprefs.currentTrip:
		add_a_current_trip(userprefs)
		userprefs.put()
	return userprefs.currentTrip

# Helper function to get the current user prefs.  Always use this helper.
def get_userprefs(user_id=None):
	if not user_id:
		user = users.get_current_user()
		if not user:
			return None
		user_id = user.user_id()
	userprefs = memcache.get(user_id, namespace='UserPrefs')
	if not userprefs:
		key = db.Key.from_path('UserPrefs', user_id)
		userprefs = db.get(key)
		if userprefs:
			userprefs.cache_set()
		else:
			userprefs = UserPrefs(key_name=user_id)
	return userprefs

# Adds a trip to the user prefs.  Creates a trip if necessary.
def add_a_current_trip(userprefs):
	query = db.Query(TripMember)
	query.filter("emailAddress =", userprefs.user.email().lower())
	query.order('-when')
	mostRecentTripMemberEntityForEmail = query.get()
	if mostRecentTripMemberEntityForEmail:
		userprefs.currentTrip = mostRecentTripMemberEntityForEmail.key().parent()
	else:
		userprefs.currentTrip = create_a_default_trip(userprefs)

# Creates a default trip when there are not trips for this email.
def create_a_default_trip(userprefs):
	trip = Trip(name = "Default Solo Trip")
	trip.put()
	member = get_trip_member(trip.key(), userprefs.user.email().lower())
	member.emailAddress=userprefs.user.email().lower()
	member.displayName=userprefs.user.nickname()
	member.phoneNumber=""
	member.put();
	return trip

# Gets tripMember data when you know the trip id and the email address
def get_trip_member(trip_key=None, email=None):
	if not trip_key or not email:
		return None
	tripMember = memcache.get("trip:" + str(trip_key.id()) + "email:" + str(email), namespace='TripMember')
	if not tripMember:
		key = db.Key.from_path('Trip', trip_key.id(), 'TripMember', email)
		tripMember = db.get(key)
		if tripMember:
			tripMember.cache_set()
		elif trip_key and email:
			tripMember = TripMember(
							key_name=email.lower(), 
			        parent=trip_key,
							emailAddress=email.lower())
	return tripMember
		