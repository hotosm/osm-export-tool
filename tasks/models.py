# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid
import os

from django.contrib.auth.models import User
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
from jobs.models import Job, HDXExportRegion
from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse


class ExportRun(models.Model):
    """
    Model for one execution of an Export - associated with a storage directory on filesystem.
    """
    id = models.AutoField(primary_key=True, editable=False)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    job = models.ForeignKey(Job, related_name='runs')
    user = models.ForeignKey(User, related_name="runs", default=0)

    status = models.CharField(
        blank=True, max_length=20,
        db_index=True, default=''
    )
    started_at = models.DateTimeField(default=timezone.now, editable=False)
    finished_at = models.DateTimeField(editable=False, null=True)

    class Meta:
        db_table = 'export_runs'
        ordering = ['created_at']

    def __str__(self):
        return '{0}'.format(self.uid)

    @property
    def duration(self):
        if self.started_at and self.finished_at:
            return (self.finished_at - self.started_at).seconds
        return None

    @property
    def elapsed_time(self):
        return (self.finished_at or timezone.now()) - self.started_at

    @property
    def size(self):
        return sum(map(
            lambda task: task.filesize_bytes or 0, self.tasks.all()))


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
    filesize_bytes = models.IntegerField(null=True)
    filenames = ArrayField(models.TextField(null=True),default=list)

    class Meta:
        db_table = 'export_tasks'
        ordering = ['created_at']

    def __str__(self):
        return 'ExportTask uid: {0}'.format(self.uid)

    @property
    def duration(self):
        if self.started_at and self.finished_at:
            return (self.finished_at - self.started_at).seconds
        return None

    @property
    def download_urls(self):
        def fdownload(fname):
            try:
                filesize_bytes = os.path.getsize(os.path.join(settings.EXPORT_DOWNLOAD_ROOT, str(self.run.uid), fname)),
            except Exception:
                filesize_bytes = 0

            return {
                "filename":fname,
                "filesize_bytes": filesize_bytes,
                "download_url":os.path.join(settings.EXPORT_MEDIA_ROOT,str(self.run.uid), fname)
            }
        return map(fdownload, self.filenames)



class ExportRunAdmin(admin.ModelAdmin):

    def start(self, request, queryset):
        from task_runners import run_task_remote
        for run in queryset:
            run_task_remote.delay(str(run.uid))

    list_display = ['uid','status','user']
    readonly_fields = ('uid','user','created_at','job')
    search_fields = ['uid']
    actions = [start]

class ExportTaskAdmin(admin.ModelAdmin):
    pass

class ExportRunsInline(admin.TabularInline):
    model = ExportRun
    readonly_fields = ('uid','user','status','created_at','change_link')
    extra = 0

    def change_link(self, obj):
        return mark_safe('<a href="%s">Link</a>' % \
                        reverse('admin:tasks_exportrun_change',
                        args=(obj.id,)))



class JobAdmin(OSMGeoAdmin):
    """
    Admin model for editing Jobs in the admin interface.
    """
    def simplified_geom_raw(self, obj):
        return obj.simplified_geom.json

    search_fields = ['uid', 'name', 'user__username']
    list_display = ['uid', 'name', 'user']
    exclude = ['the_geom']
    raw_id_fields = ("user",)
    readonly_fields=('simplified_geom_raw',)
    inlines = [ExportRunsInline]

class HDXExportRegionAdmin(admin.ModelAdmin):
    raw_id_fields = ("job",)


admin.site.register(Job, JobAdmin)
admin.site.register(HDXExportRegion, HDXExportRegionAdmin)
admin.site.register(ExportRun, ExportRunAdmin)
admin.site.register(ExportTask, ExportTaskAdmin)
