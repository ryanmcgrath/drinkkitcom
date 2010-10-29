import urllib2
from urllib2 import HTTPError

try:
	# Python 2.6 and up
	import json as simplejson
except ImportError:
	# This case gets rarer by the day, but if we need to, we can pull it from Django provided it's there.
	from django.utils import simplejson

from datetime import datetime, timedelta

from django.contrib.gis.geos import *
from django.contrib.gis.measure import D

from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext, Context
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from drinkkit.redditors.models import LocationCategory, Location, Tip, Checkin

def home(request):
	"""
		Main page shows the checkins that have occured over the past day or so. Paginate it
		so we don't completely crush things.
	"""
	queryset = Checkin.objects.filter(timestamp__gte = datetime.now() + timedelta(days=-1))
	paginator = Paginator(queryset, 15)
	
	try:	
		page = int(request.GET.get('page', '1'))
	except ValueError:
		page = 1
	
	try:
		checkins = paginator.page(page)
	except (EmptyPage, InvalidPage):
		checkins = paginator.page(paginator.num_pages)
	
	return render_to_response('locations/home.html', 
		context_instance = RequestContext(request, {'checkins': checkins})
	)

def register(request):
	"""
		Registration junk for a new user.
	"""
	if request.POST:
		form = UserCreationForm(request.POST)
		if form.is_valid():
			# Create User and junk
			new_user = form.save()
			return HttpResponseRedirect('/')
		else:
			# You done goofed
			return render_to_response('registration/register.html',
				context_instance = RequestContext(request, {'form': form})
			)
	else:
		form = UserCreationForm()
		return render_to_response('registration/register.html', 
			context_instance = RequestContext(request, {'form': form})
		)

def nearby_locations(request):
	"""
		This is a bit of an interesting method. To deal with older phones,
		we employ a somewhat odd trick here.

		We first direct the phone to a page that grabs their coordinates (whether
		by geolocation API, or IP location). We do this for phones where we can go ahead and
		get the IP location, but they might not support AJAX requests or some shit like that.

		The page then submits automatically with JS after it gets the coordinates, with a button
		for the user to hit if the browser is also gonna hang on stupid shit like that.
	"""
	if request.POST:
		if not request.POST['lat'] or not request.POST['long']:
			return render_to_response('locations/get_coords_nearby.html',
				context_instance = RequestContext(request, {
					'error': "Seems we're unable to get ahold of the GPS/location for where you are. Try again in a few minutes!"
				})
			)
		
		searchpnts = fromstr('POINT(%s %s)' % (request.POST['lat'], request.POST['long']), srid=4326)
		nearby = Location.objects.filter(geometry__distance_lte=(searchpnts, D(mi=2)))
		return render_to_response('locations/show_nearby.html',
			context_instance = RequestContext(request, {'nearby': nearby})
		)
	else:
		return render_to_response('locations/get_coords_nearby.html', 
			context_instance = RequestContext(request)
		)

def find_locations(request):
	"""
		A weak and very basic search. Should be rewritten down the road if this goes anywhere.
	"""
	if request.POST:
		queryset = Location.objects.filter(name__icontains = request.POST['search_query'])
		paginator = Paginator(queryset, 10)
		performed_search = False
		
		try:	
			page = int(request.GET.get('page', '1'))
		except ValueError:
			page = 1
		
		try:
			results = paginator.page(page)
			performed_search = True
		except (EmptyPage, InvalidPage):
			results = paginator.page(paginator.num_pages)
		
		return render_to_response('locations/search.html',
			context_instance = RequestContext(request, {
				'search_query': request.POST['search_query'], 
				'results': results,
				'performed_search': performed_search # sucks, but whatever for now
			})
		)
	else:
		return render_to_response('locations/search.html',
			context_instance = RequestContext(request)
		)

@login_required
def checkin_location(request, location_id):
	"""
		Check a user into a location.
	"""
	try:
		location = Location.objects.get(id = location_id)
	except Location.DoesNotExist:
		return HttpResponse(status=400)
	
	if request.POST:
		new_checkin = Checkin()
		new_checkin.user = request.user
		new_checkin.location = location
		new_checkin.estimated_time_here = request.POST['estimated_time_here']
		new_checkin.identify_by = request.POST['identify_by']
		new_checkin.save()
		return HttpResponseRedirect('/locations/%s/' % location_id)
	else:
		return render_to_response('locations/checkin.html', 
			context_instance = RequestContext(request, {'location': location})
		)

@login_required
def add_location(request):
	"""
		Add a new location to be checked into by others.
	
		Fairly custom logic, kind of ugly, 5:30AM, I don't care right now. None of these form fields are bound,
		but considering that only two of them are mandatory, I'm fine with this for a first release. It should be
		fixed at some point. ;P
	"""	
	if request.POST:
		# Somewhat ugly, but meh.
		if request.POST['location_name'] and (request.POST['street_address'] or (request.POST['lat'] and request.POST['long'])):
				new_location = Location()
				new_location.name = request.POST['location_name']
				
				if request.POST['lat'] and request.POST['long']:
					new_location.geometry = 'POINT(%s %s)' %(request.POST['lat'], request.POST['long'])
				else:
					# If we don't have a lat/long pair, we know they got here by providing a street address, so
					# let's do some geocoding via Google APIs and find the lat/long ourselves.
					# 
					# Note: We assume Washington, DC here because of the region this application is suited to. If
					# you wanted to expand on this, you'd probably wanna get the region/IP-(lat/long) (which isn't as accurate)
					# and use it to sandbox your results. This is a pretty hacky 5AM thing. ;P
					fixed_address = request.POST['street_address'].replace(" ", "+")
					api_url = "http://maps.googleapis.com/maps/api/geocode/json?&address=%s,Washington,DC&sensor=false" % fixed_address
					
					try:
						# Download and parse the JSON response into native Python objects.
						geocode_request = urllib2.Request(api_url)
						geocoded_data = simplejson.load(urllib2.urlopen(geocode_request))
						
						# Store latitude and longitude, for readability
						for result in geocoded_data["results"]:
							latitude = result["geometry"]["location"]["lat"]
							longitude = result["geometry"]["location"]["lng"]
						
						# Save our determined geometry coordinates
						new_location.geometry = 'POINT(%s %s)' %(latitude, longitude)
					except HTTPError:
						# You're boned, Google's either blocking you or you done goofed. Ordinarily, you'd
						# wanna handle errors properly here, but in my case I want a hard failure. YMMV.
						pass

				# If they've supplied a street address, sweet, use it.
				if request.POST['street_address']:
					new_location.street_address = request.POST['street_address']
			
				# If they set a location type/category, let's record it... (5AM code)
				if request.POST['location_type']:
					try:
						category = LocationCategory.objects.get(id = request.POST['location_type'])
						new_location.category = category
					except LocationCategory.DoesNotExist:
						pass
			
				new_location.save()
				return HttpResponseRedirect('/locations/%s/' % str(new_location.id))
		else:
			if not request.POST['lat'] or not request.POST['lat']:
				errmsg = "We weren't able to get coordinates for where you are right now. Does your phone or device have GPS? If not, specify an address and we'll use that instead!"
			if not request.POST['location_name']:
				errmsg = "You didn't even bother to enter a name for this location. Wtf?"
			return render_to_response('locations/add.html',
				context_instance = RequestContext(request, {'error': errmsg, 'category_choices': LocationCategory.objects.all()})
			)
	else:
		return render_to_response('locations/add.html',
			context_instance = RequestContext(request, {'category_choices': LocationCategory.objects.all()})
		)

def view_location(request, location_id):
	"""
		Serve up information about a location.
	
		Note: this could probably be more efficient.
	"""
	try:
		location = Location.objects.get(id = location_id)
		
		checkins = location.checkin_set
		recent_checkins = checkins.all().reverse()[:5]
		
		allow_checkin = True
		
		# Only one checkin in a day long period.
		if request.user.is_authenticated():
			if checkins.filter(user = request.user).filter(timestamp__gte = datetime.now() + timedelta(days=-1)):
				allow_checkin = False
		
		return render_to_response('locations/view.html',
			context_instance = RequestContext(request, {
				'location': location, 
				'recent_checkins': recent_checkins, 
				'allow_checkin': allow_checkin
			})
		)
	except Location.DoesNotExist:
		return HttpResponse(status=404)
		
@login_required
def add_tip(request, location_id):
	"""
		Add a new tip about a location.
	"""
	if request.POST:
		try:
			location = Location.objects.get(id = location_id)
			
			new_tip = Tip()
			new_tip.tip = request.POST['tip_body']
			new_tip.user = request.user
			new_tip.location = location
			new_tip.save()
			
			return HttpResponseRedirect('/locations/%s/' % location.id)
		except Location.DoesNotExist:
			return HttpResponse(status=404)
	else:
		return HttpResponse(status=404)
		
def view_redditor(request, redditor_name):
	"""
		View a Redditor "profile" - right now, all we do is show their checkin
		history (where they've been). Stalking is fun, right?

		...right? 
	"""
	try:
		redditor = User.objects.get(username = redditor_name)
		return render_to_response('redditors/view_profile.html',
			context_instance = RequestContext(request, {'redditor': redditor})
		)
	except User.DoesNotExist:
		return HttpResponse(status=404)
