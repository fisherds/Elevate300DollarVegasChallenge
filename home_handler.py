#!/usr/bin/env python
# Handles html generation for elevate300.appspot.com when users are logged in AND when no one is logged in.
# There is a hidden parameter called 'flush' that can be used to flush the memcache.
# fisherds@gmail.com (Dave Fisher)

from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
import logging
import userprefs

	
class HomeHandler(webapp.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/html'
		if self.request.get('flush'):
			logging.info("Flushing the entire memcache")
			memcache.flush_all()
		# Determine if a user is logged in or not and render appropriate page.
		user = users.get_current_user()
		if not user:
			values = {'login_link': users.create_login_url(self.request.path)}
			self.response.out.write(template.render('templates/home_not_logged_in.html', values))
		else:
			currentTrip = userprefs.get_users_current_trip()
			values = {'logout_link': users.create_logout_url(self.request.path),
								'name': user.nickname(),
								'current_trip_name': currentTrip.trip_name} # I believe this trigger automatic dereferencing of the Reference key
			self.response.out.write(template.render('templates/home_logged_in.html', values))	

def main():
	application = webapp.WSGIApplication([('/', HomeHandler)], debug=True)
	util.run_wsgi_app(application)

if __name__ == '__main__':
	main()
