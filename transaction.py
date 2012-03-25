#!/usr/bin/env python
# Model object to represent a single transaction model object.
# fisherds@gmail.com (Dave Fisher)

from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext.db import polymodel
import logging

CHALLENGE_TYPE_300_DOLLAR_CHALLENGE = 0
CHALLENGE_TYPE_SECOND_CHANCE = 1
CHALLENGE_TYPE_INDIVIDUAL_ONLY = 2
CHALLENGE_VALUES = [CHALLENGE_TYPE_300_DOLLAR_CHALLENGE, CHALLENGE_TYPE_SECOND_CHANCE, CHALLENGE_TYPE_INDIVIDUAL_ONLY]
CHALLENGE_TYPES = ["$300 Challenge", "2nd Chance", "Individual Only"]


#class TripEvent(polymodel.PolyModel):
class TripEvent(db.Model):
	email_address = db.StringProperty(required=True)
	challenge_type = db.IntegerProperty(choices=CHALLENGE_VALUES, default=CHALLENGE_TYPE_INDIVIDUAL_ONLY)
	notes = db.StringProperty(indexed=False, default='')
	created_by_user = db.UserProperty(auto_current_user_add=True)
	created_date_time = db.DateTimeProperty(auto_now_add=True)
	last_edited_by_user = db.UserProperty(auto_current_user=True)
	last_edited_date_time = db.DateTimeProperty(auto_now=True)	


# Entity that stores a property indicating if an Add On has been used.
#   Child of a trip entity.  The id for entities will be auto generated.  Stored in the memcache by the key's id.

# The key_name for entities will be the standardized email address.
# Note that the trip parent will make Members unique.
class AddOn(TripEvent):
	used_add_on = db.BooleanProperty(default=False)
	
	def cache_set(self):
		logging.info("Memcache: Set " + str(self.key().kind()) + " with key " + str(self.key().id()))
		memcache.set(str(self.key().id()), self, namespace=self.key().kind())

	def put(self):
		db.Model.put(self)
		self.cache_set()
		
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


# Attempts to get a single AddOn from memcache, then the datastore. Creates a new AddOn with False if not found.
def get_add_on(trip_key, email_address, challenge_type):
	standardized_email_address = standardize_email_address(email_address)
	keyName = standardized_email_address + '_type_' + str(challenge_type)
	addOn = memcache.get("trip_id:" + str(trip_key.id()) + "key_name:" + keyName, namespace='AddOn')
	if addOn:
		logging.info('Memcache: Retrieved AddOn for ' + "trip_id:" + str(trip_key.id()) + "key_name:" + keyName)
	else:
		key = db.Key.from_path('Trip', trip_key.id(), 'AddOn', keyName)
		addOn = db.get(key)
		if addOn:
			logging.info('Datastore: Retrieved AddOn for ' + "trip_id:" + str(trip_key.id()) + "key_name:" + keyName)
			addOn.cache_set()
		else:
			logging.info('New: Created AddOn for ' + "trip_id:" + str(trip_key.id()) + "key_name:" + keyName)
			tripEntity = trip.get_trip(trip_key.id())
			addOn = tripEntity.create_add_on(keyName)
	return addOn
			
# Entity that stores a single gambling transaction.  Each transaction is a
#   child of a trip entity.  The id for entities will be auto generated.  Stored in the memcache by the key's id.
class Transaction(TripEvent):
	amount = db.FloatProperty(default=0)
	casino = db.StringProperty(default='')
	game_played = db.StringProperty(default='')
	
	def cache_set(self):
		logging.info("Memcache: Set " + str(self.key().kind()) + " with key " + str(self.key().id()))
		memcache.set(str(self.key().id()), self, namespace=self.key().kind())

	def put(self):
		db.Model.put(self)
		self.cache_set()

# Attempts to get a single transaction from memcache, then the datastore. Returns None if not found.
# Currently this function is not used.  Written just for practice.
def get_trip_transaction(trip_key, transaction_id):
	transaction = memcache.get(str(transaction_id), namespace='Transaction')
	if transaction:
		logging.info('Memcache: Retrieved Transaction for transaction_id ' + str(transaction_id))
	else:
		key = db.Key.from_path('Trip', trip_key.id(), 'Transaction', transaction_id)
		transaction = db.get(key)
		if transaction:
			logging.info('Datastore: Retrieved Transaction for transaction_id ' + str(transaction_id))
			transaction.cache_set()
		else:
			logging.warning('Error: Failed to retrieved Transaction for transaction_id ' + str(transaction_id))
	return transaction
