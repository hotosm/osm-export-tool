from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from django.contrib.gis.geos import GEOSGeometry

from .models import ExportConfig, ExportFormat, ExportProfile, Job, Region

admin.site.register(ExportFormat)
admin.site.register(ExportProfile)


class HOTRegionGeoAdmin(OSMGeoAdmin):
    """
    Admin model to allow Region editing in admin interface.

    Uses OSM for base layer in map in admin.
    """
    model = Region
    exclude = ['the_geom', 'the_geog']

    def save_model(self, request, obj, form, change):  # pragma no cover
        geom_merc = obj.the_geom_webmercator
        obj.the_geom = geom_merc.transform(ct=4326, clone=True)
        obj.the_geog = GEOSGeometry(obj.the_geom.wkt)
        obj.save()


class JobAdmin(OSMGeoAdmin):
    """
    Admin model for editing Jobs in the admin interface.
    """
    search_fields = ['uid', 'name', 'user__username']
    list_display = ['uid', 'name', 'user']
    exclude = ['the_geom', 'the_geog']


class ExportConfigAdmin(admin.ModelAdmin):
    """
    Admin model for editing export configurations in the admin interface.
    """
    search_fields = ['uid', 'name', 'user__username']
    list_display = ['uid', 'name', 'user', 'config_type', 'published', 'created_at']

# register the new admin models
admin.site.register(Region, HOTRegionGeoAdmin)
admin.site.register(Job, JobAdmin)
admin.site.register(ExportConfig, ExportConfigAdmin)
