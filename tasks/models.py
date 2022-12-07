# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid
import os
from hurry.filesize import size

from django.contrib.auth.models import User
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
from jobs.models import Job, HDXExportRegion, SavedFeatureSelection, PartnerExportRegion
from django.contrib import admin
from django.contrib.gis.admin import GeoModelAdmin
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
import validators
import time

import csv
from django.http import HttpResponse

def export_as_csv(self, request, queryset):

    meta = self.model._meta
    field_names = [field.name for field in meta.fields]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
    writer = csv.writer(response)

    writer.writerow(field_names)
    for obj in queryset:
        row = writer.writerow([getattr(obj, field) for field in field_names])

    return response

class ExportCsvMixin:
    def export_as_csv(self, request, queryset):

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]
        property_names = [name for name in dir(self.model) if isinstance(getattr(self.model, name), property)]
        field_names.extend(property_names)
        exclude_fileds=['feature_selection','the_geom','simplified_geom','osma_link']
        for field in exclude_fileds:
            if field in field_names:
                field_names.remove(field)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected"

class ExportRun(models.Model):
    """
    Model for one execution of an Export - associated with a storage directory on filesystem.
    """
    id = models.AutoField(primary_key=True, editable=False)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    job = models.ForeignKey(Job, related_name='runs')
    user = models.ForeignKey(User, related_name="runs", default=0)
    worker_message_id = models.CharField(max_length=50,null=True,blank=True, editable=False) # used to store worker message id for run to abort
    hdx_sync_status =  models.BooleanField(default=False)
    status = models.CharField(
        blank=True, max_length=20,
        db_index=True, default=''
    )
    started_at = models.DateTimeField(null=True, editable=False)
    finished_at = models.DateTimeField(editable=False, null=True)

    class Meta:
        db_table = 'export_runs'
        ordering = ['created_at']

    def __str__(self):
        return '{0}'.format(self.uid)
    @property
    def export_formats(self):
        return self.job.export_formats

    @property
    def name(self):
        return self.job.name

    @property
    def is_hdx(self):
        if HDXExportRegion.objects.filter(job_id=self.job.id).exists():
            return True
        return False

    @property
    def duration(self):
        if self.started_at and self.finished_at :
            return ((self.finished_at or timezone.now()) - self.started_at).total_seconds()
        return None

    @property
    def run_duration(self):
        if self.started_at and self.finished_at:
            return time.strftime('%H:%M:%S', time.gmtime((self.finished_at - self.started_at).total_seconds()))
        return None

    @property
    def elapsed_time(self):
        return ((self.finished_at or timezone.now()) - (self.started_at or self.created_at))

    @property
    def size(self):
        return sum(map(
            lambda task: task.filesize_bytes or 0, self.tasks.all()))

    @property
    def run_size(self):
        if self.size:
            return size(self.size)

class ExportTask(models.Model):
    """
    Model for one export format within one export run.
    """
    id = models.AutoField(primary_key=True, editable=False)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    run = models.ForeignKey(ExportRun, related_name='tasks')
    status = models.CharField(blank=True, max_length=20, db_index=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    started_at = models.DateTimeField(editable=False, null=True)
    finished_at = models.DateTimeField(editable=False, null=True)
    filesize_bytes = models.BigIntegerField(null=True)
    filenames = ArrayField(models.TextField(null=True),default=list)

    class Meta:
        db_table = 'export_tasks'
        ordering = ['created_at']

    def __str__(self):
        return 'ExportTask uid: {0}'.format(self.uid)

    def username(self):
        return self.run.user

    @property
    def duration(self):
        if self.started_at and self.finished_at:
            return (self.finished_at  or timezone.now() - self.started_at).total_seconds()
        return None


    @property
    def task_duration(self):
        if self.started_at and self.finished_at:
            return time.strftime('%H:%M:%S', time.gmtime((self.finished_at - self.started_at).total_seconds()))
        return None

    
    @property
    def task_size(self):
        if self.filesize_bytes:
            return size(self.filesize_bytes)

    @property
    def download_urls(self):
        def fdownload(fname):
            valid=validators.url(fname)
            if valid==True:
                download_url = fname
                absolute_download_url=download_url
                try :
                    value = download_url.split('/')
                    name=value[-1]
                    split_name=name.split('_uid_')
                    file_name=split_name[0]
                    
                    if file_name[-(2*len(self.name)+1):] == f"{self.name}_{self.name}":  
                        # filename has duplicated export formats
                        file_name=file_name[:-(2*len(self.name)+2)]
                    download_name=f"{file_name}.zip"  # getting human redable name ignoring unique id
                    fname=download_name
                except:
                    fname=f"""{self.run.job.name}_{self.name}.zip"""
                try:
                    with open(os.path.join(settings.EXPORT_DOWNLOAD_ROOT, str(self.run.uid),f"{name}_size.txt")) as f :
                        size=f.readline()
                    filesize_bytes=int(size)
                except:
                    filesize_bytes=0

            else:
                try:
                    filesize_bytes = os.path.getsize(os.path.join(settings.EXPORT_DOWNLOAD_ROOT, str(self.run.uid), fname).encode('utf-8'))
                except Exception:
                    filesize_bytes = 0
                download_url = os.path.join(settings.EXPORT_MEDIA_ROOT,str(self.run.uid), fname)
                absolute_download_url=settings.HOSTNAME + download_url
            return {
                "filename":fname,
                "filesize_bytes": filesize_bytes,
                "download_url":download_url,
                "absolute_download_url":absolute_download_url
            }
        return map(fdownload, self.filenames)



class ExportRunAdmin(admin.ModelAdmin,ExportCsvMixin):

    def start(self, request, queryset):
        from tasks.task_runners import run_task_async_ondemand
        for run in queryset:
            run_task_async_ondemand.send(str(run.uid))

    list_display = ['uid','job_ui_link','name','status','export_formats','is_hdx','user','created_at','run_duration','started_at','run_size']
    list_filter = ('status',)
    readonly_fields = ('uid','user','created_at')
    raw_id_fields = ('job',)
    search_fields = ['uid']
    actions = [start]
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    actions = ["export_as_csv"]

    def job_ui_link(self, obj):
        return mark_safe(f"""<a href="https://{settings.HOSTNAME}/en/v3/exports/{obj.job.uid}" target="_blank">UI Job Link</a>""")



    def job_link(self, obj):
        return mark_safe('<a href="%s">Link to Job</a>' % \
                        reverse('admin:jobs_job_change',
                        args=(obj.job.id,)))

class ExportTaskAdmin(admin.ModelAdmin):
    list_display = ['uid','run','name','status','created_at','username','task_size','task_duration']
    search_fields = ['uid','run__uid']
    list_filter = ('name','status')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

class ExportRunsInline(admin.TabularInline):
    model = ExportRun
    readonly_fields = ('uid','user','status','created_at','change_link')
    extra = 0

    def change_link(self, obj):
        return mark_safe('<a href="%s">Link</a>' % \
                        reverse('admin:tasks_exportrun_change',
                        args=(obj.id,)))



class JobAdmin(GeoModelAdmin,ExportCsvMixin):
    """
    Admin model for editing Jobs in the admin interface.
    """
    def simplified_geom_raw(self, obj):
        return obj.simplified_geom.json

    search_fields = ['uid', 'name', 'user__username']
    list_display = ['uid', 'name', 'user','is_hdx','export_formats','last_run_date','last_run_status','created_at', 'updated_at','area']
    list_filter = ('pinned',)
    exclude = ['the_geom']
    raw_id_fields = ("user",)
    readonly_fields=('simplified_geom_raw',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    inlines = [ExportRunsInline]
    actions = ["export_as_csv"]


class HDXExportRegionAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ['name','job_link','edit_link','schedule_period','last_run_hum','last_run_status','last_run_hdx_sync','next_run_hum','last_export_size',"last_run_duration",'export_formats','country_export','schedule_hour','is_private','locations','created_by']
    list_filter = ('schedule_period','schedule_hour','country_export','is_private')
    raw_id_fields = ("job",)
    search_fields = ['job__name','job__description', 'job__uid']
    ordering = ('job__updated_at',)
    actions = ["export_as_csv"]

    def job_link(self, obj):
        return mark_safe(f"""<a href="https://{settings.HOSTNAME}/en/v3/exports/{obj.job.uid}" target="_blank">UI Job Link</a>""")

    def edit_link(self, obj):
        return mark_safe(f"""<a href="https://{settings.HOSTNAME}/en/v3/hdx/edit/{obj.id}" target="_blank">Edit HDX Job</a>""")



class PartnerExportRegionAdmin(admin.ModelAdmin):
    raw_id_fields = ('job',)

class SavedFeatureSelectionAdmin(admin.ModelAdmin):
    raw_id_fields = ("user",)
    search_fields = ['name','description']
    list_filter = ('pinned',)
    list_display = [ 'name', 'description']

admin.site.register(Job, JobAdmin)
admin.site.register(HDXExportRegion, HDXExportRegionAdmin)
admin.site.register(PartnerExportRegion, PartnerExportRegionAdmin)
admin.site.register(ExportRun, ExportRunAdmin)
admin.site.register(ExportTask, ExportTaskAdmin)
admin.site.register(SavedFeatureSelection, SavedFeatureSelectionAdmin)
