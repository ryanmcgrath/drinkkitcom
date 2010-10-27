from django.contrib import admin
from drinkkit.redditors.models import LocationCategory, Location, Checkin, Tip

class CheckinInline(admin.StackedInline):
	model = Checkin
	extra = 1

class TipInline(admin.StackedInline):
	model = Tip
	extra = 1

class LocationAdmin(admin.ModelAdmin):
	inlines = [CheckinInline, TipInline]

admin.site.register(Location, LocationAdmin)
admin.site.register(LocationCategory)
