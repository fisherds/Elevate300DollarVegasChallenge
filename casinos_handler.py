#!/usr/bin/env python
# Finds the closest casinos to the given locatoin
# fisherds@gmail.com (Dave Fisher)

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
import logging
import math
import userprefs

	
class CasinosHandler(webapp.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/html'
		latitude = float(self.request.get('latitude'))
		longitude = float(self.request.get('longitude'))
		selectCasino = self.request.get('selectcasino')
		count = int(self.request.get('count', default_value="6"))
		
		logging.info("latitude " + str(latitude))
		logging.info("longitude " + str(longitude))
		
		if selectCasino:
			logging.info("Yes, there is a select casino and it is " + selectCasino)
		else:
			logging.info("No select casino")
			casinoOptions = self.getCasinoOptions()
			sortedCasinoOptions = self.sortCasinoOptions(casinoOptions, latitude, longitude)
			nearestCasinos = []
			allCasinos = []
			for casinoOption in sortedCasinoOptions:
				if len(nearestCasinos) < count:
					nearestCasinos.append(casinoOption['name'])
				allCasinos.append(casinoOption['name'])
		self.response.out.write("{'nearest_casinos': " + str(nearestCasinos) + ", 'all_casinos': " + str(allCasinos) + '}')	

	def sortCasinoOptions(self, casinoOptions, latitude, longitude):
		for casinoOption in casinoOptions:
			distanceAway = self.getDistance(latitude, casinoOption['latitude'], longitude, casinoOption['longitude'])
			casinoOption['distance_away'] = distanceAway
			logging.info(casinoOption['name'] + " is a distance away = " + str(casinoOption['distance_away']))
		sortedCasinoOptions = sorted(casinoOptions, key=lambda casinoOption: casinoOption['distance_away'])
		return sortedCasinoOptions
		
	def getDistance(self, latitude1, latitude2, longitude1, longitude2):
		# From http://www.movable-type.co.uk/scripts/latlong.html
		R = 6371 # km of the earth radius
		dLat = (latitude2 - latitude1) / 180 * math.pi
		dLon = (longitude2 - longitude1) / 180 * math.pi
		latitude1 = latitude1 / 180 * math.pi
		latitude2 = latitude2 / 180 * math.pi

		a = math.sin(dLat/2) * math.sin(dLat/2) + math.sin(dLon/2) * math.sin(dLon/2) * math.cos(latitude1) * math.cos(latitude2)
		c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
		return R * c
	
	def getCasinoOptions(self):
		casinoOptions = []
		casinoOptions.append({'name': 'Fisher apt', 'latitude': 37.3958385, 'longitude': -122.0937384})
		casinoOptions.append({'name': 'Braggs', 'latitude': 37.368008, 'longitude': -122.104883})
		casinoOptions.append({'name': 'B45', 'latitude': 37.420370, 'longitude': -122.082245})
		casinoOptions.append({'name': 'B46 Gym', 'latitude': 37.419032, 'longitude': -122.082374})
		casinoOptions.append({'name': 'Victorian Deli', 'latitude': 37.419948, 'longitude': -122.086285})
		casinoOptions.append({'name': 'Parking Spot', 'latitude': 37.41974, 'longitude': -122.081623})
		
		casinoOptions.append({'name': 'Aria', 'latitude': 36.107075, 'longitude': -115.177488})
		casinoOptions.append({'name': "Bally's", 'latitude': 36.113939, 'longitude': -115.170386})
		casinoOptions.append({'name': 'Bellagio', 'latitude': 36.113168, 'longitude': -115.175879})
		casinoOptions.append({'name': "Caesar's Palace", 'latitude': 36.11647, 'longitude': -115.175074})
		casinoOptions.append({'name': 'Casino Royale', 'latitude': 36.120734, 'longitude': -115.171748})
		casinoOptions.append({'name': 'Circus Circus', 'latitude': 36.137286, 'longitude': -115.164764})
		casinoOptions.append({'name': 'Cosmopolitan', 'latitude': 36.109779, 'longitude': -115.174055})
		casinoOptions.append({'name': 'Encore', 'latitude': 36.124669, 'longitude': -115.171148})
		casinoOptions.append({'name': 'Excalibur', 'latitude': 36.099221, 'longitude': -115.175192})
		casinoOptions.append({'name': 'Flamingo', 'latitude': 36.116106, 'longitude': -115.171888})
		casinoOptions.append({'name': 'Gold Coast', 'latitude': 36.116661, 'longitude': -115.192841})
		casinoOptions.append({'name': 'Golden Nugget', 'latitude': 36.16991, 'longitude': -115.143746})
		casinoOptions.append({'name': 'Hard Rock', 'latitude': 36.109398, 'longitude': -115.153778})
		casinoOptions.append({'name': "Harrah's", 'latitude': 36.119486, 'longitude': -115.171545})
		casinoOptions.append({'name': 'Hilton', 'latitude': 36.136818, 'longitude': -115.1522})
		casinoOptions.append({'name': 'Hooters', 'latitude': 36.100019, 'longitude': -115.167521})
		casinoOptions.append({'name': 'Imperial Palace', 'latitude': 36.118412, 'longitude': -115.17104})
		casinoOptions.append({'name': 'Luxor', 'latitude': 36.095545, 'longitude': -115.175858})
		casinoOptions.append({'name': 'Mandalay Bay', 'latitude': 36.092199, 'longitude': -115.175986})
		casinoOptions.append({'name': 'MGM Grand', 'latitude': 36.1017, 'longitude': -115.171824})
		casinoOptions.append({'name': 'Mirage', 'latitude': 36.121263, 'longitude': -115.174077})
		casinoOptions.append({'name': 'Monte Carlo', 'latitude': 36.104648, 'longitude': -115.174828})
		casinoOptions.append({'name': 'New York New York', 'latitude': 36.101614, 'longitude': -115.173878})
		casinoOptions.append({'name': 'Palazzo', 'latitude': 36.124339, 'longitude': -115.168562})
		casinoOptions.append({'name': 'Paris', 'latitude': 36.112501, 'longitude': -115.171545})
		casinoOptions.append({'name': 'Planet Hollywood', 'latitude': 36.110004, 'longitude': -115.170611})
		casinoOptions.append({'name': 'Rio', 'latitude': 36.116869, 'longitude': -115.187252})
		casinoOptions.append({'name': 'Riviera', 'latitude': 36.124669, 'longitude': -115.171148})
		casinoOptions.append({'name': 'Stratosphere', 'latitude': 36.147544, 'longitude': -115.15558})
		casinoOptions.append({'name': 'The Orleans', 'latitude': 36.102446, 'longitude': -115.201778})
		casinoOptions.append({'name': 'The Palms', 'latitude': 36.114269, 'longitude': -115.196135})
		casinoOptions.append({'name': 'Treasure Island', 'latitude': 36.124669, 'longitude': -115.171148})
		casinoOptions.append({'name': 'Tropicana', 'latitude': 36.099689, 'longitude': -115.171695})
		casinoOptions.append({'name': 'Venetian', 'latitude': 36.122199, 'longitude': -115.169924})
		casinoOptions.append({'name': 'Wynn', 'latitude': 36.124669, 'longitude': -115.171148})
		return casinoOptions
		
def main():
	application = webapp.WSGIApplication([('/casinos', CasinosHandler)], debug=True)
	util.run_wsgi_app(application)

if __name__ == '__main__':
	main()
