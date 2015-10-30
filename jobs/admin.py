from django.contrib import admin
from django.template import RequestContext  
from django.conf.urls import patterns, url
from django.contrib import messages
from django.shortcuts import render_to_response
from django.contrib.contenttypes.models import ContentType
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
    list_display = ['uid', 'name', 'user', 'region']
    exclude = ['the_geom', 'the_geog']
    actions = ['select_exports']
    
    update_template = 'admin/update_regions.html'
    update_complete_template = 'admin/update_complete.html'
    
    def select_exports(self, request, queryset):
        """
        Select exports to update.
        """
        selected = ','.join(request.POST.getlist(admin.ACTION_CHECKBOX_NAME))
        regions = Region.objects.all()
        
        return render_to_response(self.update_template, {
            'regions': regions,
            'selected': selected,
            'opts': self.model._meta,
        }, context_instance=RequestContext(request))
    
    select_exports.short_description = "Assign a region to the selected exports"
    
    def update_exports(self, request):
        """
        Update selected exports.
        """
        selected = request.POST.get('selected','')
        num_selected = len(selected.split(','))
        region_uid = request.POST.get('region','')
        region = Region.objects.get(uid=region_uid)
        for id in selected.split(','):
            export = Job.objects.get(id=id)
            export.region = region
            export.save()
            
        messages.success(request, '{0} exports updated.'.format(num_selected))
        return render_to_response(self.update_complete_template, {
            'num_selected': len(selected.split(',')),
            'region': region.name,
            'opts': self.model._meta,
        }, context_instance=RequestContext(request))

    def get_urls(self):
        urls = super(JobAdmin, self).get_urls()
        update_urls = patterns('',
            url(r'^select/$', self.admin_site.admin_view(self.select_exports)),
            url(r'^update/$', self.admin_site.admin_view(self.update_exports), name="update_regions"),
        )
        return update_urls + urls



class ExportConfigAdmin(admin.ModelAdmin):
    """
    Admin model for editing export configurations in the admin interface.
    """
    search_fields = ['uid', 'name', 'user__username']
    list_display = ['uid', 'name', 'user', 'config_type']


# register the new admin models
admin.site.register(Region, HOTRegionGeoAdmin)
admin.site.register(Job, JobAdmin)
admin.site.register(ExportConfig, ExportConfigAdmin)
