"""Provides classes for handling API requests."""
# -*- coding: utf-8 -*-
from distutils.util import strtobool
from itertools import chain
import logging

import dateutil.parser
import requests
from cachetools.func import ttl_cache
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Permission
from django.contrib.gis.geos import GEOSGeometry, Polygon
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from jobs.models import HDXExportRegion, Job, SavedFeatureSelection
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import detail_route
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from api.serializers import (ConfigurationSerializer, ExportRunSerializer,
                         HDXExportRegionListSerializer,
                         HDXExportRegionSerializer, JobGeomSerializer,
                         JobSerializer)
from tasks.models import ExportRun
from tasks.task_runners import ExportTaskRunner

from .permissions import IsHDXAdmin, IsOwnerOrReadOnly
from .renderers import HOTExportApiRenderer

# Get an instance of a logger
LOG = logging.getLogger(__name__)

# controls how api responses are rendered
renderer_classes = (JSONRenderer, HOTExportApiRenderer)


def bbox_to_geom(s):
    try:
        return GEOSGeometry(Polygon.from_bbox(s.split(',')), srid=4326)
    except Exception:
        raise ValidationError({'bbox': 'Query bounding box is malformed.'})


class JobViewSet(viewsets.ModelViewSet):
    """
    ##Export API Endpoint.

    Main endpoint for export creation and managment. Provides endpoints
    for creating, listing and deleting export jobs.

    Updates to existing jobs are not supported as exports can be cloned.

    Request data should be posted as `application/json`.

    <code>
    curl -v -H "Content-Type: application/json" -H "Authorization: Token [your token]"
    --data @request.json http://EXPORT_TOOL_URL/api/jobs
    </code>

    To monitor the resulting export run retreive the `uid` value from the returned json
    and call http://export.hotosm.org/api/runs?job_uid=[the returned uid]
    """

    serializer_class = JobSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly)
    lookup_field = 'uid'
    filter_backends = (filters.OrderingFilter, filters.SearchFilter, )
    search_fields = ('name', 'description', 'event', 'user__username')
    ordering_fields = ('__all__',)
    ordering = ('-updated_at')

    def get_queryset(self):
        user = self.request.user
        queryset = Job.objects
        all = strtobool(self.request.query_params.get('all', 'false')) or self.action != "list"
        bbox = self.request.query_params.get('bbox', None)
        before = self.request.query_params.get('before', None)
        after = self.request.query_params.get('after', None)

        if before is not None:
            queryset = queryset.filter(Q(created_at__lte=before))

        if after is not None:
            queryset = queryset.filter(Q(created_at__gte=after))

        if bbox is not None:
            bbox = bbox_to_geom(bbox)
            queryset = queryset.filter(Q(the_geom__within=bbox))

        if not all:
            queryset = queryset.filter(Q(user_id=user.id))

        return queryset.filter(Q(user_id=user.id) | Q(published=True))

    def perform_create(self, serializer):
        job = serializer.save()
        task_runner = ExportTaskRunner()
        task_runner.run_task(job_uid=str(job.uid))

    @detail_route()
    def geom(self, request, uid=None):
        job = Job.objects.get(uid=uid)
        geom_serializer = JobGeomSerializer(job)
        return Response(geom_serializer.data)


class ConfigurationViewSet(viewsets.ModelViewSet):
    """ API endpoints for stored YAML configurations.
    Note that these are mutable - a configuration can be edited."""

    serializer_class = ConfigurationSerializer
    permission_classes = (IsOwnerOrReadOnly,
                          permissions.IsAuthenticatedOrReadOnly)
    lookup_field = 'uid'
    filter_backends = (filters.OrderingFilter, filters.SearchFilter, )
    search_fields = ('name', 'description')
    ordering_fields = ('__all__')

    def get_queryset(self):
        user = self.request.user
        queryset = SavedFeatureSelection.objects.filter(deleted=False).order_by('-pinned','name')
        all = strtobool(self.request.query_params.get('all', 'false')) or self.action != "list"

        if not all:
            queryset = queryset.filter(Q(user_id=user.id))

        return queryset.filter(Q(user_id=user.id) | Q(public=True))


class ExportRunViewSet(viewsets.ModelViewSet):
    """
    Export Run API Endpoint.

    Poll this endpoint for querying export runs.
    """
    serializer_class = ExportRunSerializer
    permission_classes = (permissions.AllowAny, )
    lookup_field = 'uid'

    def create(self, request, format='json'):
        """
        runs the job.
        """
        job_uid = request.query_params.get('job_uid', None)
        task_runner = ExportTaskRunner()
        task_runner.run_task(job_uid=job_uid, user=request.user)
        return Response({'status': 'OK'}, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        return ExportRun.objects.all().order_by('-started_at')

    def retrieve(self, request, uid=None, *args, **kwargs):
        """
        Get a single Export Run.
        """
        queryset = ExportRun.objects.filter(uid=uid)
        serializer = self.get_serializer(
            queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        """
        List the Export Runs for a single Job.
        """
        job_uid = self.request.query_params.get('job_uid', None)
        queryset = self.filter_queryset(
            ExportRun.objects.filter(job__uid=job_uid).order_by('-started_at'))
        serializer = self.get_serializer(
            queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class HDXExportRegionViewSet(viewsets.ModelViewSet):
    """ API endpoint for HDX regions.
    Viewing and editing these is limited to a set of admins."""

    ordering_fields = '__all__'
    ordering = ('job__description',)
    permission_classes = (IsHDXAdmin, )
    filter_backends = (filters.OrderingFilter, filters.SearchFilter, )
    search_fields = ('job__name', 'job__description')

    def get_queryset(self):
        return HDXExportRegion.objects.filter(deleted=False).prefetch_related(
            'job__runs__tasks').defer('job__the_geom')

    def get_serializer_class(self):
        if self.action == "list":
            return HDXExportRegionListSerializer

        return HDXExportRegionSerializer

    def perform_create(self, serializer):
        serializer.save()
        if settings.SYNC_TO_HDX:
            serializer.instance.sync_to_hdx()
        else:
            print("Stubbing interaction with HDX API.")

    def perform_update(self, serializer):
        serializer.save()
        if settings.SYNC_TO_HDX:
            serializer.instance.sync_to_hdx()
        else:
            print("Stubbing interaction with HDX API.")


@require_http_methods(['GET'])
@login_required()
def request_geonames(request):
    """Geocode with GeoNames."""
    payload = {
        'maxRows': 20,
        'username': 'osm_export_tool',
        'style': 'full',
        'q': request.GET.get('q')
    }

    geonames_url = getattr(settings, 'GEONAMES_API_URL')

    if geonames_url:
        response = requests.get(geonames_url, params=payload).json()
        assert (isinstance(response, dict))
        return JsonResponse(response)
    else:
        return JsonResponse(
            {
                'error': 'A url was not provided for geonames'
            },
            status=500, )


@ttl_cache(ttl=60)
@require_http_methods(['GET'])
@login_required()
def get_overpass_timestamp(request):
    """
    Endpoint to show the last OSM update timestamp on the Create page.
    this sometimes fails, returning a HTTP 200 but empty content.
    """
    r = requests.get('{}timestamp'.format(settings.OVERPASS_API_URL))
    return JsonResponse({'timestamp': dateutil.parser.parse(r.content)})

@login_required()
def get_overpass_status(request):
    r = requests.get('{}status'.format(settings.OVERPASS_API_URL))
    return HttpResponse(r.content)


@require_http_methods(['GET'])
@login_required()
def get_user_permissions(request):
    user = request.user
    permissions = []

    if user.is_superuser:
        permissions = Permission.objects.all().values_list(
            'content_type__app_label', 'codename')
    else:
        permissions = chain(
            user.user_permissions.all().values_list('content_type__app_label',
                                                    'codename'),
            Permission.objects.filter(group__user=user).values_list(
                'content_type__app_label', 'codename'))

    return JsonResponse({
        "username": user.username,
        "permissions":
        list(map(lambda pair: ".".join(pair), (set(permissions))))
    })
