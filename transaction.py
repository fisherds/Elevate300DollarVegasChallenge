#!/usr/bin/env python
# Model object to represent a single transaction model object.
# fisherds@gmail.com (Dave Fisher)

from google.appengine.api import memcache
from google.appengine.ext import db
import logging

CHALLENGE_TYPE_PRACTICE = 0
CHALLENGE_TYPE_300_DOLLAR_CHALLENGE = 1
CHALLENGE_TYPE_SECOND_CHANCE = 2
CHALLENGE_TYPE_INDIVIDUAL_ONLY = 3
CHALLENGE_VALUES = [CHALLENGE_TYPE_PRACTICE, CHALLENGE_TYPE_300_DOLLAR_CHALLENGE, CHALLENGE_TYPE_SECOND_CHANCE, CHALLENGE_TYPE_INDIVIDUAL_ONLY]
CHALLENGE_TYPES = ["Practice", "$300 Challenge", "2nd Chance", "Individual Only"]

# Entity that stores a single gambling transaction.  Each transaction is a
#   child of a trip entity.  The id for entities will be auto generated.
class Transaction(db.Model):
	email_address = db.StringProperty(required=True)
	challenge_type = db.IntegerProperty(choices=CHALLENGE_VALUES, default=CHALLENGE_TYPE_INDIVIDUAL_ONLY)
	amount = db.FloatProperty(default=0)
	casino = db.StringProperty(default='')
	game_played = db.StringProperty(default='')
	notes = db.StringProperty(indexed=False, default='')
	created_by_user = db.UserProperty(auto_current_user_add=True)
	created_date_time = db.DateTimeProperty(auto_now_add=True)
	last_edited_by_user = db.UserProperty(auto_current_user=True)
	last_edited_date_time = db.DateTimeProperty(auto_now=True)
	
	def cache_set(self):
		logging.info("Memcache: Set " + str(self.key().kind()) + " with key " + str(self.key().id()))
		memcache.set(str(self.key().id()), self, namespace=self.key().kind())
		#memcache.delete(str(self.parent().key().id()) + "_alltransactions") # Remove the trip's _alltransactions memcache
		#TODO: Move to a smart update of the memcache instead of just completely dropping the data

	def put(self):
		db.Model.put(self)
		self.cache_set()

# Attempts to get a single transaction from memcache, then the datastore. Returns None if not found.
# Currently this function is not used.  Written just for practice.
def get_trip_transaction(trip_key, transaction_id):
	transaction = memcache.get(str(transaction_id), namespace='Transaction')
	if transaction:
		logging.info('Memcache: Retrieved Transaction for transaction_id ' + transaction_id)
	else:
		key = db.Key.from_path('Trip', trip_key.id(), 'Transaction', transaction_id)
		transaction = db.get(key)
		if transaction:
			logging.info('Datastore: Retrieved Transaction for transaction_id ' + transaction_id)
			transaction.cache_set()
		else:
			logging.warning('Error: Failed to retrieved Transaction for transaction_id ' + transaction_id)
	return transaction
