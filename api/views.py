"""Provides classes for handling API requests."""
# -*- coding: utf-8 -*-
from distutils.util import strtobool
import itertools
from itertools import chain
import logging
import json
from django.utils import timezone
from datetime import datetime, timedelta
from collections import Counter
import os
import io
import pickle
import csv
import dateutil.parser
import requests
from cachetools.func import ttl_cache
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Permission
from django.contrib.auth.models import Group
from django.contrib.gis.geos import GEOSGeometry, Polygon
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.http import (
    JsonResponse,
    HttpResponse,
    HttpResponseNotFound,
    HttpResponseForbidden,
)
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError as DjangoValidationError
from jobs.models import HDXExportRegion, PartnerExportRegion, Job, SavedFeatureSelection
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import detail_route
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from api.serializers import (
    ConfigurationSerializer,
    ExportRunSerializer,
    ExportTaskSerializer,
    HDXExportRegionListSerializer,
    HDXExportRegionSerializer,
    JobGeomSerializer,
    PartnerExportRegionListSerializer,
    PartnerExportRegionSerializer,
    JobSerializer,
)
from tasks.models import ExportRun, ExportTask
from tasks.task_runners import ExportTaskRunner

from .permissions import IsHDXAdmin, IsOwnerOrReadOnly, IsMemberOfGroup
from .renderers import HOTExportApiRenderer

from hdx_exports.hdx_export_set import sync_region
from rtree import index
import psutil

import asyncio

# Get an instance of a logger
LOG = logging.getLogger(__name__)

# controls how api responses are rendered
renderer_classes = (JSONRenderer, HOTExportApiRenderer)

DIR = os.path.dirname(os.path.abspath(__file__))
try:
    idx = index.Rtree(os.path.join(DIR, "reverse_geocode"))
except Exception as ex:
    # pass
    raise ex


def bbox_to_geom(s):
    try:
        return GEOSGeometry(Polygon.from_bbox(s.split(",")), srid=4326)
    except Exception:
        raise ValidationError({"bbox": "Query bounding box is malformed."})


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
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)
    lookup_field = "uid"
    filter_backends = (
        filters.OrderingFilter,
        filters.SearchFilter,
    )
    search_fields = ("name", "description", "event", "user__username")
    ordering_fields = ("__all__",)
    ordering = ("-pinned", "-updated_at")

    def get_queryset(self):
        user = self.request.user
        queryset = Job.objects
        all = (
            strtobool(self.request.query_params.get("all", "false"))
            or self.action != "list"
        )
        bbox = self.request.query_params.get("bbox", None)
        before = self.request.query_params.get("before", None)
        after = self.request.query_params.get("after", None)
        pinned = self.request.query_params.get("pinned", None)

        if before is not None:
            queryset = queryset.filter(Q(created_at__lte=before))

        if after is not None:
            queryset = queryset.filter(Q(created_at__gte=after))

        if bbox is not None:
            bbox = bbox_to_geom(bbox)
            queryset = queryset.filter(Q(the_geom__within=bbox))

        if pinned:
            queryset = queryset.filter(Q(pinned=True))

        if not all:
            queryset = queryset.filter(Q(user_id=user.id))

        if user.is_superuser:
            return queryset

        return queryset

    def perform_create(self, serializer):
        if (
            Job.objects.filter(
                created_at__gt=timezone.now() - timedelta(minutes=60),
                user=self.request.user,
            ).count()
            > 5
        ):
            raise ValidationError(
                {"the_geom": ["You are rate limited to 5 exports per hour."]}
            )
        job = serializer.save()
        task_runner = ExportTaskRunner()
        task_runner.run_task(job_uid=str(job.uid))

    @detail_route()
    def geom(self, request, uid=None):
        job = Job.objects.get(uid=uid)
        geom_serializer = JobGeomSerializer(job)
        return Response(geom_serializer.data)


class ConfigurationViewSet(viewsets.ModelViewSet):
    """API endpoints for stored YAML configurations.
    Note that these are mutable - a configuration can be edited."""

    serializer_class = ConfigurationSerializer
    permission_classes = (IsOwnerOrReadOnly, permissions.IsAuthenticatedOrReadOnly)
    lookup_field = "uid"
    filter_backends = (
        filters.OrderingFilter,
        filters.SearchFilter,
    )
    search_fields = ("name", "description")
    ordering_fields = "__all__"
    ordering = "-pinned"

    def get_queryset(self):
        user = self.request.user
        queryset = SavedFeatureSelection.objects.filter(deleted=False).order_by(
            "-pinned", "name"
        )
        pinned = self.request.query_params.get("pinned", None)
        all = (
            strtobool(self.request.query_params.get("all", "false"))
            or self.action != "list"
        )

        if not all:
            queryset = queryset.filter(Q(user_id=user.id))
        if pinned:
            queryset = queryset.filter(Q(pinned=True))

        return queryset.filter(Q(user_id=user.id) | Q(public=True))


class ExportRunViewSet(viewsets.ModelViewSet):
    """
    Export Run API Endpoint.

    Poll this endpoint for querying export runs.
    """

    serializer_class = ExportRunSerializer
    permission_classes = (permissions.AllowAny,)
    lookup_field = "uid"

    def create(self, request, format="json"):
        """
        runs the job.
        """
        if (
            ExportRun.objects.filter(
                created_at__gt=timezone.now() - timedelta(minutes=1), user=request.user
            ).count()
            >= 1
        ):
            return Response(
                {"status": "RATE_LIMITED"}, status=status.HTTP_400_BAD_REQUEST
            )

        job_uid = request.query_params.get("job_uid", None)
        if Job.objects.get(uid=job_uid).last_run_status == "SUBMITTED":
            return Response(
                {"status": "PREVIOUS_RUN_IN_QUEUE"}, status=status.HTTP_400_BAD_REQUEST
            )
        task_runner = ExportTaskRunner()
        task_runner.run_task(job_uid=job_uid, user=request.user)
        return Response({"status": "OK"}, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        return ExportRun.objects.all().order_by("-started_at")

    def retrieve(self, request, uid=None, *args, **kwargs):
        """
        Get a single Export Run.
        """
        queryset = ExportRun.objects.filter(uid=uid)
        serializer = self.get_serializer(
            queryset, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        """
        List the Export Runs for a single Job.
        """
        job_uid = self.request.query_params.get("job_uid", None)
        queryset = self.filter_queryset(
            ExportRun.objects.filter(job__uid=job_uid).order_by("-started_at")
        )
        serializer = self.get_serializer(
            queryset, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class HDXExportRegionViewSet(viewsets.ModelViewSet):
    """API endpoint for HDX regions.
    Viewing and editing these is limited to a set of admins."""

    ordering_fields = "__all__"
    ordering = ("job__description",)
    permission_classes = (IsHDXAdmin,)
    filter_backends = (
        filters.OrderingFilter,
        filters.SearchFilter,
    )
    search_fields = ("job__name", "job__description")

    def get_queryset(self):
        queryset = HDXExportRegion.objects.filter(deleted=False)
        schedule_period = self.request.query_params.get("schedule_period", None)
        if schedule_period not in [None, "any"]:
            queryset = queryset.filter(Q(schedule_period=schedule_period))

        return queryset.prefetch_related("job__runs__tasks").defer("job__the_geom")

    def get_serializer_class(self):
        if self.action == "list":
            return HDXExportRegionListSerializer

        return HDXExportRegionSerializer

    def perform_create(self, serializer):

        serializer.save()
        if settings.SYNC_TO_HDX:
            sync_region(serializer.instance)
        else:
            print("Stubbing interaction with HDX API.")

    def perform_update(self, serializer):
        serializer.save()
        if settings.SYNC_TO_HDX:
            sync_region(serializer.instance)
        else:
            print("Stubbing interaction with HDX API.")


class PartnerExportRegionViewSet(viewsets.ModelViewSet):
    # get only Regions that belong to the user's Groups.
    ordering_fields = "__all__"
    ordering = ("job__description",)
    filter_backends = (
        filters.OrderingFilter,
        filters.SearchFilter,
    )
    search_fields = ("job__name", "job__description")
    permission_classes = (IsMemberOfGroup,)

    def get_queryset(self):
        group_ids = self.request.user.groups.values_list("id")
        return (
            PartnerExportRegion.objects.filter(deleted=False, group_id__in=group_ids)
            .prefetch_related("job__runs__tasks")
            .defer("job__the_geom")
        )

    def get_serializer_class(self):
        if self.action == "list":
            return PartnerExportRegionListSerializer

        return PartnerExportRegionSerializer


@require_http_methods(["GET"])
def permalink(request, uid):
    try:
        job = Job.objects.filter(uid=uid).first()
        if not job:
            return HttpResponseNotFound()
        run = job.runs.filter(status="COMPLETED").latest("finished_at")
        serializer = ExportTaskSerializer(run.tasks.all(), many=True)
        return HttpResponse(JSONRenderer().render(serializer.data))
    except ExportRun.DoesNotExist:
        return HttpResponse(JSONRenderer().render({}))
    except DjangoValidationError:
        return HttpResponseNotFound()


@require_http_methods(["GET"])
def stats(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    before = request.GET.get("before", timezone.now())
    after = request.GET.get("after", timezone.now() - timedelta(days=1))
    period = request.GET.get("period", "day")
    is_csv = request.GET.get("csv", False) == "true"

    def toWeek(dt):
        sunday = dt.strftime("%Y-%U-0")
        return datetime.strptime(sunday, "%Y-%U-%w").strftime("%Y-%m-%d")

    def toDay(dt):
        return dt.strftime("%Y-%m-%d")

    def toMonth(dt):
        return dt.strftime("%Y-%m")

    if period == "day":
        period_fn = toDay
    elif period == "week":
        period_fn = toWeek
    elif period == "month":
        period_fn = toMonth

    users = (
        User.objects.only("date_joined")
        .filter(date_joined__gte=after, date_joined__lte=before)
        .order_by("-date_joined")
    )

    grouped_users_by_period = {}
    for gu in itertools.groupby(users, lambda u: period_fn(u.date_joined)):
        grouped_users_by_period[gu[0]] = len(list(gu[1]))

    queryset = Job.objects.only("created_at", "the_geom").order_by("-created_at")
    if before:
        queryset = queryset.filter(Q(created_at__lte=before))
    if after:
        queryset = queryset.filter(Q(created_at__gte=after))

    grouped_jobs = itertools.groupby(queryset, lambda j: period_fn(j.created_at))

    geoms = []
    periods = []
    for x in grouped_jobs:
        top_regions = Counter()
        jobs_in_group = list(x[1])
        for j in jobs_in_group:
            centroid = j.the_geom.centroid
            geoms.append([centroid.x, centroid.y])
            result = next(idx.nearest((centroid.x, centroid.y), 1, objects=True))
            top_regions[result.object[2]] += 1

        users_in_period = grouped_users_by_period.get(x[0], 0)

        top_regions_string = " ".join(
            ["{0}:{1}".format(x[0], x[1]) for x in top_regions.most_common(5)]
        )
        periods.append(
            {
                "start_date": x[0],
                "jobs_count": len(jobs_in_group),
                "users_count": users_in_period,
                "top_regions": top_regions_string,
            }
        )

    if is_csv:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["start_date", "jobs_count", "users_count", "top_regions"])
        for period in periods:
            writer.writerow(
                [
                    period["start_date"],
                    period["jobs_count"],
                    period["users_count"],
                    period["top_regions"],
                ]
            )
        return HttpResponse(output.getvalue())
    else:
        return HttpResponse(json.dumps({"periods": periods, "geoms": geoms}))


@require_http_methods(["GET"])
def run_stats(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    before = request.GET.get("before", timezone.now())
    after = request.GET.get("after", timezone.now() - timedelta(days=1))
    period = request.GET.get("period", "day")
    is_csv = request.GET.get("csv", False) == "true"

    def toWeek(dt):
        sunday = dt.strftime("%Y-%U-0")
        return datetime.strptime(sunday, "%Y-%U-%w").strftime("%Y-%m-%d")

    def toDay(dt):
        return dt.strftime("%Y-%m-%d")

    def toMonth(dt):
        return dt.strftime("%Y-%m")

    if period == "day":
        period_fn = toDay
    elif period == "week":
        period_fn = toWeek
    elif period == "month":
        period_fn = toMonth

    run_queryset = ExportRun.objects.only("started_at", "status").order_by(
        "-started_at"
    )

    if before:
        run_queryset = run_queryset.filter(Q(started_at__lte=before))
    if after:
        run_queryset = run_queryset.filter(Q(started_at__gte=after))

    grouped_runs = itertools.groupby(run_queryset, lambda j: period_fn(j.started_at))

    periods = []
    for x in grouped_runs:
        run_types = Counter()
        export_formats = Counter()
        hdx_run_status = Counter()
        normal_run_status = Counter()
        runs_in_group = list(x[1])
        for j in runs_in_group:
            result = j.is_hdx
            if result is True:
                result = "hdx_run"
                hdx_status = j.status
                hdx_run_status[hdx_status.lower()] += 1
            else:
                result = "on_demand"
                normal_status = j.status
                normal_run_status[normal_status.lower()] += 1
            run_types[result] += 1
            export_format = j.export_formats
            for f in export_format:
                export_formats[str(f)] += 1
        run_types_string = ",".join(
            ["{0}:{1}".format(x[0], x[1]) for x in run_types.most_common(5)]
        )
        export_formats_string = ",".join(
            ["{0}:{1}".format(x[0], x[1]) for x in export_formats.most_common(10)]
        )
        hdx_run_status_string = ",".join(
            ["{0}:{1}".format(x[0], x[1]) for x in hdx_run_status.most_common(4)]
        )
        normal_run_status_string = ",".join(
            ["{0}:{1}".format(x[0], x[1]) for x in normal_run_status.most_common(4)]
        )

        periods.append(
            {
                "start_date": x[0],
                "runs_count": len(runs_in_group),
                "run_types": run_types_string,
                "hdx_run_status": hdx_run_status_string,
                "normal_run_status": normal_run_status_string,
                "export_formats": export_formats_string,
            }
        )

    if is_csv:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                "start_date",
                "runs_count",
                "run_types",
                "hdx_run_status",
                "normal_run_status",
                "export_formats",
            ]
        )
        for period in periods:
            writer.writerow(
                [
                    period["start_date"],
                    period["runs_count"],
                    period["run_types"],
                    period["hdx_run_status"],
                    period["normal_run_status"],
                    period["export_formats"],
                ]
            )
        return HttpResponse(output.getvalue())
    else:
        return HttpResponse(json.dumps({"periods": periods}))


@require_http_methods(["GET"])
@login_required()
def request_nominatim(request):
    """Country boundaries using nominatim"""

    nominatim_url = getattr(settings, "NOMINATIM_API_URL")
    if nominatim_url is None:
        error_dict = {
            "error": "A url was not provided for nominatim",
            "status": 500,
        }
        return JsonResponse(error_dict)

    country = request.GET.get("country", None)
    if country is None:
        error_dict = {
            "error": "Missing country request parameter",
            "status": 400,
        }
        return JsonResponse(error_dict)

    country_code = request.GET.get("countryCode", None)
    if country_code is None:
        error_dict = {
            "error": "Missing countryCode request parameter",
            "status": 400,
        }
        return JsonResponse(error_dict)

    params = {
        "country": country,
        "countryCodes": country_code,
        "polygon_geojson": 1,
        "format": "json",
    }

    response = requests.get(nominatim_url, params=params)
    if response.status_code != 200:
        error_dict = {
            "error": "Invalid Status code from nominatim url",
            "status": 400,
        }
        return JsonResponse(error_dict)

    try:
        data = response.json()
    except json.decoder.JSONDecodeError:
        error_dict = {
            "error": "Response content not serializable to json",
            "status": 400,
        }
        return JsonResponse(error_dict)

    feature = {"type": "Feature", "geometry": data[0].get("geojson")}

    feature_collection = {"type": "FeatureCollection", "features": [feature]}

    return JsonResponse(feature_collection)


@require_http_methods(["GET"])
@login_required()
def request_geonames(request):
    """Geocode with GeoNames."""
    payload = {
        "maxRows": 20,
        "username": "osm_export_tool",
        "style": "full",
        "q": request.GET.get("q"),
    }

    geonames_url = getattr(settings, "GEONAMES_API_URL")
    tm_url = getattr(settings, "TASKING_MANAGER_API_URL")
    RAW_DATA_API_URL = getattr(settings, "RAW_DATA_API_URL")

    if geonames_url:
        keyword = request.GET.get("q")
        response = {'totalResultsCount': 0, 'geonames': []}
        if not (str(keyword).lower().startswith('boundary') or str(keyword).lower().startswith('osm') or str(keyword).lower().startswith('tm')):
            response = requests.get(geonames_url, params=payload).json()
            print(response)
        assert isinstance(response, dict)
        if RAW_DATA_API_URL:
            if str(keyword).lower().startswith('boundary'):
                lst=keyword.split(" ")
                if len(lst)>1:
                    keyword=lst[1]
                    res = requests.get(f"{RAW_DATA_API_URL}v1/countries/?q={keyword}")
                    if res.ok:
                        if len(res.json()["features"]) >= 1:
                            for feature in res.json()["features"]:
                                geojson = {
                                        "type": "FeatureCollection",
                                        "features": [
                                            {"type": "Feature", "properties": {}, "geometry":feature["geometry"]}
                                        ],
                                    }
                                add_resp = {
                                    "bbox": geojson,
                                    "adminName2": feature["properties"]["description"],
                                    "name": f'{request.GET.get("q")} -> {feature["properties"]["name"]}',
                                    "countryName": feature["properties"]["dataset_name"],
                                    "adminName1": feature["properties"]["id"],
                                }
                
                                if "geonames" in response:
                                    response["geonames"].append(add_resp)

            if str(keyword).lower().startswith('osm'):
                lst=keyword.split(" ")
                if len(lst)>1:
                    keyword=lst[1]
                    try : 
                        osm_id= int(keyword) 
                        res = requests.get(f"{RAW_DATA_API_URL}v1/osm_id/?osm_id={osm_id}")
                        if res.ok:
                            if len(res.json()["features"]) >= 1:
                                for feature in res.json()["features"]:
                                    geojson = {
                                            "type": "FeatureCollection",
                                            "features": [
                                                {"type": "Feature", "properties": {}, "geometry": feature["geometry"]}
                                            ],
                                        }
                                    add_resp = {
                                        "bbox": geojson,
                                        "adminName2": "OSM",
                                        "name": request.GET.get("q"),
                                        "countryName": osm_id,
                                        "adminName1": "Element",
                                    }
                    
                                    if "geonames" in response:
                                        response["geonames"].append(add_resp)
                    except :
                        pass


        if str(keyword).lower().startswith('tm'):
                lst=keyword.split(" ")
                if len(lst)>1:

                    keyword=lst[1]
                    if tm_url:
                        tm_res = requests.get(f"{tm_url}/{int(keyword)}/")
                        if tm_res.ok:
                            tm_res=tm_res.json()
                            if "areaOfInterest" in tm_res:
                                print("TM Project found")
                                geom = tm_res["areaOfInterest"]
                                geojson = {
                                    "type": "FeatureCollection",
                                    "features": [
                                        {"type": "Feature", "properties": {}, "geometry": geom}
                                    ],
                                }

                                add_resp = {
                                    "bbox": geojson,
                                    "adminName2": "TM",
                                    "name": request.GET.get("q"),
                                    "countryName": "Boundary",
                                    "adminName1": "Project",
                                }
                                # print(add_resp)
                                if "geonames" in response:
                                    response["geonames"].append(add_resp)

        return JsonResponse(response)
    else:
        return JsonResponse(
            {"error": "A url was not provided for geonames"},
            status=500,
        )


@ttl_cache(ttl=60)
@require_http_methods(["GET"])
@login_required()
def get_overpass_timestamp(request):
    """
    Endpoint to show the last OSM update timestamp on the Create page.
    this sometimes fails, returning a HTTP 200 but empty content.
    """
    r = requests.get("{}timestamp".format(settings.OVERPASS_API_URL))
    return JsonResponse({"timestamp": dateutil.parser.parse(r.content)})


@login_required()
def get_overpass_status(request):
    r = requests.get("{}status".format(settings.OVERPASS_API_URL))
    return HttpResponse(r.content)


@require_http_methods(["GET"])
@login_required()
def get_user_permissions(request):
    user = request.user
    permissions = []

    if user.is_superuser:
        permissions = Permission.objects.all().values_list(
            "content_type__app_label", "codename"
        )
    else:
        permissions = chain(
            user.user_permissions.all().values_list(
                "content_type__app_label", "codename"
            ),
            Permission.objects.filter(group__user=user).values_list(
                "content_type__app_label", "codename"
            ),
        )

    return JsonResponse(
        {
            "username": user.username,
            "permissions": list(map(lambda pair: ".".join(pair), (set(permissions)))),
        }
    )


# get a list of partner organizations and their numeric IDs.
# this can be exposed to the public.
@require_http_methods(["GET"])
@login_required()
def get_groups(request):
    groups = [
        {"id": g.id, "name": g.name} for g in Group.objects.filter(is_partner=True)
    ]
    return JsonResponse({"groups": groups})


async def sync_to_hdx_api_async(run_uid):
    try:
        run = ExportRun.objects.get(uid=run_uid)
    except ExportRun.DoesNotExist:
        return {"error": "Invalid run UID"}

    try:
        region = HDXExportRegion.objects.get(job_id=run.job_id)
    except HDXExportRegion.DoesNotExist:
        return JsonResponse({"error": "HDXExportRegion not found"}, status=404)

    public_dir = os.path.join(settings.EXPORT_DOWNLOAD_ROOT, run_uid)
    LOG.debug(public_dir)
    pickle_file_path = os.path.join(public_dir, 'all_zips.pkl')

    if os.path.exists(pickle_file_path):
        try:
            with open(pickle_file_path, 'rb') as file:
                all_zips_data = file.read()
            all_zips = pickle.loads(all_zips_data)
            LOG.debug("Calling hdx API")
            sync_region(region, all_zips, public_dir)
            run.hdx_sync_status = True
        except Exception as ex:
            run.sync_status = False
            LOG.error(ex)
            return JsonResponse({"error": "Sync failed"}, status=500)
    else:
        return JsonResponse({"error": "No exports available"}, status=404)
    
    run.save()
    LOG.debug('Sync Success to HDX for run: {0}'.format(run_uid))


    return {"success": "Sync to HDX completed successfully"}


@require_http_methods(["GET"])
def sync_to_hdx_api(request):
    if not request.user.is_superuser:
        return JsonResponse({"error": "Permission denied"}, status=403)
    
    run_uid = request.GET.get("run_uid")
    if run_uid:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(sync_to_hdx_api_async(run_uid))
        # asyncio.run(sync_to_hdx_api_async(run_uid))
        return JsonResponse({"message": "Sync request received and is being processed in the background."}, status=202)

    return JsonResponse({"error": "Missing run UID"}, status=400)

# @require_http_methods(["GET"])
# def sync_to_hdx_api(request):
#     if not request.user.is_superuser:
#         return HttpResponseForbidden()
    
#     run_uid = request.GET.get("run_uid")
#     if run_uid:
#         LOG.debug('Syncing to HDX for run: {0}'.format(run_uid))
#         try:
#             run = ExportRun.objects.get(uid=run_uid)
#         except ExportRun.DoesNotExist:
#             return JsonResponse({"error": "Invalid run UID"}, status=404)
        
#         try:
#             region = HDXExportRegion.objects.get(job_id=run.job_id)
#         except HDXExportRegion.DoesNotExist:
#             return JsonResponse({"error": "HDXExportRegion not found"}, status=404)

#         public_dir = os.path.join(settings.EXPORT_DOWNLOAD_ROOT, run_uid)
#         LOG.debug(public_dir)
#         pickle_file_path = os.path.join(public_dir, 'all_zips.pkl')

#         if os.path.exists(pickle_file_path):
#             try:
#                 with open(pickle_file_path, 'rb') as file:
#                     all_zips_data = file.read()
#                 all_zips = pickle.loads(all_zips_data)
#                 LOG.debug("Calling hdx API")
#                 sync_region(region, all_zips, public_dir)
#                 run.hdx_sync_status = True
#             except Exception as ex:
#                 run.sync_status = False
#                 LOG.error(ex)
#                 return JsonResponse({"error": "Sync failed"}, status=500)
#         else:
#             return JsonResponse({"error": "No exports available"}, status=404)
        
#         run.save()
#         LOG.debug('Sync Success to HDX for run: {0}'.format(run_uid))

#         return JsonResponse({"success": "Sync to HDX completed successfully"}, status=200)

#     return JsonResponse({"error": "Missing run UID"}, status=400)



from dramatiq_abort import abort


@require_http_methods(["GET"])
def cancel_run(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    run_uid = request.GET.get("run_uid")
    if run_uid:
        try:
            run = ExportRun.objects.get(uid=run_uid)
            message_id = run.worker_message_id
            if message_id:
                LOG.debug("Canceling task_message_id:{0} ".format(message_id))
                if run.status == "SUBMITTED":
                    abort(message_id, mode="cancel")
                elif run.status == "RUNNING":
                    abort(message_id)  # cancel if its in queue or in progress

            run.status = "FAILED"
            run.worker_message_id = None  # set back message id
            run.save()
        except (Job.DoesNotExist, ExportRun.DoesNotExist, ExportTask.DoesNotExist):
            LOG.warn("ExportRun doesnot exist . Exiting")
            return JsonResponse(
                {"error": "Run does not exist"},
                status=500,
            )
    return JsonResponse({"Sucess": "Run Cancelled successfully"})


@require_http_methods(["GET"])
def machine_status(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    CPU_use = psutil.cpu_percent(3)
    date_from = datetime.now() - timedelta(days=1)
    hdx_jobs = HDXExportRegion.objects.all()
    Runs_since_day = ExportRun.objects.filter(created_at__gte=date_from)
    running_runs = Runs_since_day.filter(status="RUNNING").order_by("-started_at")
    if running_runs:
        last_run_timestamp = running_runs[0].started_at
        last_run_running_from = str(timezone.now() - last_run_timestamp)
    else:
        last_run_timestamp = "N/A"
        last_run_running_from = "N/A"
    overpass = requests.get("{}timestamp".format(settings.OVERPASS_API_URL))
    galaxy = requests.get("{}v1/status/".format(settings.RAW_DATA_API_URL))

    overpass_timestamp = str(
        datetime.now(timezone.utc) - dateutil.parser.parse(overpass.content)
    )
    galaxy_timestamp = str(
        datetime.now(timezone.utc) - dateutil.parser.parse(galaxy.json()["lastUpdated"])
    )
    return JsonResponse(
        {
            "system": {
                "current_time": datetime.now(),
                "cpu_usage_%": int(CPU_use),
                "ram_used_%": (psutil.virtual_memory()[2]),
                "overpass_behind_by": overpass_timestamp,
                "rawdata_api_behind_by": galaxy_timestamp,
            },
            "runs_since_a_day": {
                "submitted": Runs_since_day.filter(status="SUBMITTED").count(),
                "running": Runs_since_day.filter(status="RUNNING").count(),
                "last_running_from": last_run_running_from,
                "failed": Runs_since_day.filter(status="FAILED").count(),
                "completed": Runs_since_day.filter(status="COMPLETED").count(),
            },
            "hdx": {
                "total_jobs": hdx_jobs.count(),
                "Running_daily": hdx_jobs.filter(schedule_period="daily").count(),
                "Running_weekly": hdx_jobs.filter(schedule_period="weekly").count(),
                "Running_monthly": hdx_jobs.filter(schedule_period="monthly").count(),
                "Running_every_2_weeks": hdx_jobs.filter(
                    schedule_period="2wks"
                ).count(),
                "Running_every_3_weeks": hdx_jobs.filter(
                    schedule_period="3wks"
                ).count(),
                "Running_every_6hrs": hdx_jobs.filter(schedule_period="6hrs").count(),
                "Disabled": hdx_jobs.filter(schedule_period="disabled").count(),
            },
        }
    )
