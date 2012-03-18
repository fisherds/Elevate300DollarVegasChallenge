#!/usr/bin/env python
# fisherds@gmail.com (Dave Fisher)

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
import datetime
import member
import userprefs
import logging

class TransactionHandler(webapp.RequestHandler):
	def get(self):
		time = datetime.datetime.now()
		self.response.headers['Content-Type'] = 'text/html'
		currentTrip = userprefs.get_users_current_trip()
		user = users.get_current_user()
		currentMember = member.get_member_for_trip(currentTrip.key(), user.email())
		now = datetime.datetime.now()
		now += datetime.timedelta(0, 0, 0, 0, 0, -7);  # TODO: Handle daylight savings time issue (-8 standard)
		# for attr in [ 'year', 'month', 'day', 'hour', 'minute', 'second', 'microsecond']:
		#     print attr, ':', getattr(now, attr)
		# format = "%a %b %d %Y at %H:%M"
		format = "%a"
		dayString = now.strftime(format)
		# notes = 'Created by ' + currentMember.display_name + ' on ' + dateString
		dateString = str(now.month) + "/" + str(now.day) + "/" + str(now.year)
		if now.hour == 0:
			hourStr = '12'
			amPm = 'am'
		elif now.hour < 12:
			hourStr = str(now.hour)
			amPm = 'am'
		elif now.hour == 12:
			hourStr = str(now.hour)
			amPm = 'pm'
		else:
			hourStr = str(now.hour - 12)
			amPm = 'pm'
		timeString =  "%s:%02d %s" % (hourStr, now.minute, amPm)
		notes = 'Created by ' + currentMember.display_name + ' on ' + dayString + ' ' + dateString + ' at ' + timeString
		# TODO: Make pretty via http://docs.python.org/library/datetime.html
		
		
		logging.info(notes)
		
		values = {'trip_members': currentTrip.get_all_members(),
				  'notes': notes}
		self.response.out.write(template.render('templates/transaction.html', values))

	def post(self):
		logging.info(self.request)
		currentTrip = userprefs.get_users_current_trip()
		try:
			gamePlayed = self.request.get('game_played_select')
			if len(gamePlayed) == 0:
				gamePlayed = self.request.get('game_played_text')
			logging.info(self.request.get('email_address'))	
			logging.info(self.request.get('challenge_type'))
			logging.info(self.request.get('amount'))	
			logging.info(self.request.get('casino'))
			logging.info(gamePlayed)
			logging.info(self.request.get('notes'))
			currentTrip.create_transaction(email_address = self.request.get('email_address'),
				challenge_type = int(self.request.get('challenge_type')),
				amount = float(self.request.get('amount')),
				casino = self.request.get('casino'),
				game_played = gamePlayed,
				notes = self.request.get('notes'))
		except:
			logging.warning("Error: Exception occurred and transaction was not added.")
		self.redirect('/transaction')

def main():
	application = webapp.WSGIApplication([('/transaction', TransactionHandler)], debug=True)
	util.run_wsgi_app(application)

if __name__ == '__main__':
	main()
