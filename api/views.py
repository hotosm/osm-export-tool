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
from rest_framework.serializers import ValidationError

from .renderers import HOTExportApiRenderer
from .errors import InvalidBBOXError
from jobs.models import Job, ExportFormat, Region
from serializers import JobSerializer, ExportFormatSerializer, RegionSerializer
from .errors import MissingFormatAPIResponse, MissingParamAPIResponse
from tasks.export_tasks import ExportTaskRunner

# Get an instance of a logger
logger = logging.getLogger(__name__)

renderer_classes = (JSONRenderer, HOTExportApiRenderer)


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json; version=1.0'
        super(JSONResponse, self).__init__(content, **kwargs)


class JobViewSet(viewsets.ModelViewSet):
    """
    ## Job API Endpoint.
    Endpoint for job creation and managment.
    
    More docs here...
    """
    serializer_class = JobSerializer
    permission_classes = (permissions.AllowAny,)
    parser_classes = (FormParser, MultiPartParser)
    lookup_field = 'uid'

    def get_queryset(self):
        return Job.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = JobSerializer(data=request.data,
                                   context={'request': request})
        if (serializer.is_valid()):
            job = serializer.save()
            # add the export formats
            formats = request.data.getlist('formats')
            for format_uid in formats:
                export_format = ExportFormat.objects.get(uid=format_uid)
                job.formats.add(export_format)
            task_runner = ExportTaskRunner()
            job_uid = str(job.uid)
            task_runner.run_task(job_uid=job_uid)
            running = JobSerializer(job, context={'request': request})
            return Response(running.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class ExportFormatViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ### ExportFormat API endpoint.
    Endpoint exposing the supported export formats.
    
    """
    serializer_class = ExportFormatSerializer
    permission_classes = (permissions.AllowAny,)
    queryset = ExportFormat.objects.all()
    lookup_field = 'slug'
    

class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ### Region API endpoint.
    Endpoint exposing the supported regions.
    """
    
    serializer_class = RegionSerializer
    permission_classes = (permissions.AllowAny,)
    queryset = Region.objects.all()
    lookup_field = 'uid'
    
    
    
