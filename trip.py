#!/usr/bin/env python
# Trip model class.
# fisherds@gmail.com (Dave Fisher)

from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext import db
import logging
import member
import transaction

# A Trip entity is the parent to TripMember and GamblingTransaction entities.
#   Generally a Trip entity should be accessed via the current_trip reference
#   property of a UserPrefs.  Then the GamblingTransactions for the Trip can
#   be accessed because they are children of this entity.
# The id for this group will be auto generated. A Trip is a root entity (no parent)
class Trip(db.Model):
	trip_name = db.StringProperty(default='Default Trip')
	created_by_user = db.UserProperty(auto_current_user_add=True)
	created_date_time = db.DateTimeProperty(auto_now_add=True)
	last_edited_by_user = db.UserProperty(auto_current_user=True)
	last_edited_date_time = db.DateTimeProperty(auto_now=True)
	
	def cache_set(self):
		logging.info("Memcache: Set " + str(self.key().kind()) + " with key " + str(self.key().id()))
		memcache.set(str(self.key().id()), self, namespace=self.key().kind())
		
	def put(self):
		db.Model.put(self)
		self.cache_set()
	
	def get_all_transactions(self):
		tripTransactions = memcache.get(str(self.key().id()) + "_alltransactions")
		if tripTransactions:
			logging.info('Memcache: Retrieved all transactions from trip id ' + str(self.key().id()))
		else:
			logging.info('Datastore: Retrieve all transactions from trip id ' + str(self.key().id()))
			tripTransactions = []
			query = db.Query(transaction.Transaction)
			query.ancestor(self.key())
			query.order('-created_date_time')
			# Could use the fetch command but that limits the max number of transactions
			# Using this slower brute force method for now
			# A faster solution would be to return the query and let the user of the query update the memcache
			# Probably this method is not actually that slow though 2 milliseconds to run I'd guess
			for aTransaction in query:
				tripTransactions.append(aTransaction)
			# Save the brute force result in memcache to make it faster next time.
			memcache.set(str(self.key().id()) + "_alltransactions", tripTransactions)
			
		return tripTransactions
	
	def create_transaction(self, email_address, challenge_type, amount, casino, game_played, notes):
		newTransaction = transaction.Transaction(
				parent = self.key(),
				email_address = email_address,
				challenge_type = challenge_type,
				amount = amount,
				casino = casino,
				game_played = game_played,
				notes = notes)
		newTransaction.put()
		logging.info('Memcache: For now delete the _alltransactions memcache value (FIX LATER)')
		memcache.delete(str(self.key().id()) + "_alltransactions") # Remove the trip's _alltransactions memcache
		return newTransaction
	
	def delete_transaction(self, transaction_key):
		pass

	def update_transaction(self, transaction_key):
		pass
	
	def get_all_members(self):
		tripMembers = memcache.get(str(self.key().id()) + "_allmembers")
		if tripMembers:
			logging.info('Memcache: Retrieved all members from trip id ' + str(self.key().id()))
		else:
			logging.info('Datastore: Retrieve all members from trip id ' + str(self.key().id()))
			tripMembers = []
			query = db.Query(member.Member)
			query.ancestor(self.key())
			query.order('created_date_time')
			# Could use the fetch command but that limits the max number of transactions
			# Using this slower brute force method for now
			# A faster solution would be to return the query and let the user of the query update the memcache
			# Probably this method is not actually that slow though 2 milliseconds to run I'd guess
			for aMember in query:
				tripMembers.append(aMember)
			# Save the brute force result in memcache to make it faster next time.
			memcache.set(str(self.key().id()) + "_allmembers", tripMembers)
		return tripMembers
	
	def create_member(self, email_address=None, display_name=None, phone_number=''):
		user = users.get_current_user()
		if not email_address:
			email_address = user.email()
		standardized_email_address = member.standardize_email_address(email_address)
		if not display_name:
			display_name = user.nickname()
		newMember = member.Member(key_name=standardized_email_address,
				parent=self.key(),
				email_address=standardized_email_address,
				display_name=display_name,
				phone_number=phone_number)
		newMember.put()
		logging.info('Memcache: For now delete the _allmembers memcache value (FIX LATER)')
		memcache.delete(str(self.key().id()) + "_allmembers")
		return newMember
	
	def delete_member(self, standardized_email_address):
		pass

	def delete_non_creator_members(self):
		# Iterate over all the members using a query.		
		query = db.Query(member.Member)
		query.ancestor(self.key())
		query.filter('email_address !=', member.standardize_email_address(self.created_by_user.email()))
		for aMember in query:
			aMember.delete()
		memcache.delete(str(self.key().id()) + "_allmembers")

	def update_member(self, standardized_email_address):
		pass
	
	def is_a_member(self, email_address=None):
		if not email_address:
			email_address = users.get_current_user().email()
		standardized_email_address = member.standardize_email_address(email_address)
		allMembers = self.get_all_members()
		for aMember in allMembers:
			if aMember.email_address == standardized_email_address:
				return True
		return False

# Always use this mechanism to get a trip when you have the trip id.
# Will return None if trip id does not exist.
def get_trip(trip_id):
	trip = memcache.get(str(trip_id), namespace='Trip')
	if trip:
		logging.info('Memcache: Retrieved trip id ' + str(trip_id))
	else:
		key = db.Key.from_path('Trip', trip_id)
		trip = db.get(key)
		if trip:
			logging.info('Datastore: Retrieved trip id ' + str(trip_id))
			trip.cache_set()
		else:
			logging.warning('Error: Failed to retrieve trip id ' + str(trip_id))
	return trip


# Creates a default trip when there are not trips for this email.
# For practice, call this function within a transaction like this:
# try:
#   db.run_in_transaction(create_default_trip)
# except db.TransactionFailedError, e:
#   # Report an error to the user.
#   # ...
def create_default_trip():
	defaultTrip = Trip(trip_name = "Default Solo Trip")
	defaultTrip.put()
	user = users.get_current_user()
	standardized_email_address = member.standardize_email_address(user.email())
	displayName = user.nickname()
	defaultTrip.create_member(standardized_email_address, displayName)
	return defaultTrip
