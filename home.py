#!/usr/bin/env python
# fisherds@gmail.com (Dave Fisher)

from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
import model
import logging
	
class HomeHandler(webapp.RequestHandler):
  def get(self):
		self.response.headers['Content-Type'] = 'text/html'
		user = users.get_current_user()
		if self.request.get('flush'):
			logging.info("Flushing the entire memcache")
			memcache.flush_all()
		if not user:
			values = {'loginLink': users.create_login_url(self.request.path)}
			self.response.out.write(template.render('templates/home_not_logged_in.html', values))
		else:
			currentTrip = model.get_current_trip()
			values = {'logoutLink': users.create_logout_url(self.request.path),
								'name': user.nickname(),
								'currentTripName': currentTrip.name}
			self.response.out.write(template.render('templates/home_logged_in.html', values))	

def main():
	application = webapp.WSGIApplication([('/', HomeHandler)], debug=True)
	util.run_wsgi_app(application)

if __name__ == '__main__':
	main()
