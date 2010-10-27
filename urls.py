from django.conf.urls.defaults import *
from django.contrib import admin

# Set up the admin shit
admin.autodiscover()

urlpatterns = patterns('',		
	(r'^admin/', include(admin.site.urls)),
	
	# Viewing and adding tips/locations
	(r'^locations/add/$', 'drinkkit.redditors.views.add_location'),
	(r'^locations/search/$', 'drinkkit.redditors.views.find_locations'),
	(r'^locations/nearby/$', 'drinkkit.redditors.views.nearby_locations'),
	
	(r'^locations/(?P<location_id>[a-zA-Z0-9_.-]+)/add_tip/$', 'drinkkit.redditors.views.add_tip'),
	(r'^locations/(?P<location_id>[a-zA-Z0-9_.-]+)/checkin/$', 'drinkkit.redditors.views.checkin_location'),
	(r'^locations/(?P<location_id>[a-zA-Z0-9_.-]+)/$', 'drinkkit.redditors.views.view_location'),

	# Registration
	(r'^register/$', 'drinkkit.redditors.views.register'),

	# User forms - password, logout, login, etc.
	(r'^password_reset/$', 'django.contrib.auth.views.password_reset'),
	(r'^unauth/$', 'django.contrib.auth.views.logout_then_login'),
	(r'^auth/$', 'django.contrib.auth.views.login'),
	(r'^/*', 'drinkkit.redditors.views.home'),
)
