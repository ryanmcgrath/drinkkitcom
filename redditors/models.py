from datetime import datetime, timedelta
from django.contrib.gis.db import models
from django.contrib.auth.models import User

class LocationCategory(models.Model):
	"""
		Table/class to hold categories for locations to fall under. Let this
		be fairly agnostic of everything.
	"""
	name = models.CharField(max_length = 200)
	
	def __str__(self):
		return "%s" % str(self.name)

class Location(models.Model):
	"""
		Locations, yo. Street Address is optional, don't make the user
		have to fuck with something they don't know offhand unless they care.

		Category is self explanatory, geometry is a GeoDjango model type to handle
		storing lat/long coordinates for distance equations.
	"""
	name = models.CharField(max_length=200)
	street_address = models.CharField(max_length=200, blank=True)
	category = models.ForeignKey(LocationCategory, blank=True, null=True)
	geometry = models.PointField(srid=4326, blank=True, null=True)
	objects = models.GeoManager()
	
	def __str__(self):
		return "%s" % str(self.name)
	
	def get_recent_checkins_count(self):
		"""
			Tally up how many checkins this location had in the past day.
		"""
		return self.checkin_set.filter(timestamp__gte = datetime.now() + timedelta(days=-1)).count()
	
	def address_for_geocode(self):
		return self.street_address.replace(" ", "+")

class Checkin(models.Model):
	"""
		Checkin model - pretty self explanatory all around.
	"""
	user = models.ForeignKey(User)
	location = models.ForeignKey(Location)
	timestamp = models.DateTimeField(auto_now=True)
	estimated_time_here = models.CharField(max_length=200, blank=True, null=True)
	identify_by = models.CharField(max_length=200, blank=True, null=True)

class Tip(models.Model):
	"""
		Tips - again, fairly self explanatory.
	"""
	tip = models.TextField(blank=False)
	user = models.ForeignKey(User)
	timestamp = models.DateTimeField(auto_now=True)
	location = models.ForeignKey(Location)
	
	def __str__(self):
		return "%s" % str(self.title)
