from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin

from .models import Job

class JobAdmin(OSMGeoAdmin):
    """
    Admin model for editing Jobs in the admin interface.
    """
    search_fields = ['uid', 'name', 'user__username']
    list_display = ['uid', 'name', 'user']
    exclude = ['the_geom']

# register the new admin models
admin.site.register(Job, JobAdmin)
