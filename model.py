#!/usr/bin/env python
# fisherds@gmail.com (Dave Fisher)

from google.appengine.ext import db

class GamblingTransaction(db.Model):
	name = db.StringProperty(default='')
	challengeType = db.IntegerProperty(default=3)
	amount = db.FloatProperty(default=0)
	casino = db.StringProperty(default='')
	gamePlayed = db.StringProperty(default='')
	notes = db.StringProperty(default='')
	when = db.DateTimeProperty(auto_now_add=True)
