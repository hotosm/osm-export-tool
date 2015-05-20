import logging
import os
import shutil
import pdb
from datetime import datetime

from django.http import HttpResponse
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from django.db.models import FileField

from rest_framework import views
from rest_framework import viewsets
from rest_framework import authentication
from rest_framework import permissions
from rest_framework import mixins
from rest_framework import status
from rest_framework import renderers
from rest_framework import generics
from rest_framework import filters
from rest_framework.reverse import reverse
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from .renderers import HOTExportApiRenderer

from jobs.models import Job, ExportFormat
from serializers import JobSerializer, ExportFormatSerializer

from tasks.export_tasks import run_export_job

# Get an instance of a logger
logger = logging.getLogger(__name__)

renderer_classes = (JSONRenderer, HOTExportApiRenderer)


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


class JobViewSet(viewsets.ModelViewSet):
    """
    Job API Endpoint
    """
    serializer_class = JobSerializer
    permission_classes = (permissions.AllowAny,)
    parser_classes = (FormParser, MultiPartParser)

    def get_queryset(self):
        return Job.objects.all()

    def create(self, request, *args, **kwargs):
        formats = request.data.getlist('formats')
        logger.debug(formats)
        serializer = JobSerializer(data=request.data,
                                   context={'request': request})
        if (serializer.is_valid()):
            job = serializer.save()
            # add the export formats
            for id in formats:
                export_format = ExportFormat.objects.get(id=id)
                job.formats.add(export_format)
            # now add the job to the queue..
            # could have logic here to determine which task to run
            res = run_export_job.delay(job.id)
            job.task_id = res.id
            job.status = res.state
            job.save()
            running = JobSerializer(job, context={'request': request})
            return Response(running.data, status=status.HTTP_201_CREATED)
        else:
            logger.debug(serializer.errors)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class ExportFormatViewSet(viewsets.ModelViewSet):
    """ExportFormat API endpoint."""

    serializer_class = ExportFormatSerializer
    permission_classes = (permissions.AllowAny,)
    parser_classes = (FormParser,)
    queryset = ExportFormat.objects.all()
