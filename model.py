#!/usr/bin/env python
# fisherds@gmail.com (Dave Fisher)

from google.appengine.ext import db

class GamblingTransaction(db.Model):
	name = db.StringProperty(required=True)
	challengeType = db.IntegerProperty(required=True)
	amount = db.FloatProperty(required=True)
	casino = db.StringProperty(required=False)
	gamePlayed = db.StringProperty(required=False)
	comment = db.StringProperty(required=False)
	when = db.DateTimeProperty(auto_now_add=True)
