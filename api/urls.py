# -*- coding: utf-8 -*-
"""API url configuration."""

from api.views import (ConfigurationViewSet, ExportRunViewSet,
                       HDXExportRegionViewSet, JobViewSet)
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from rest_framework.routers import DefaultRouter

from .views import get_overpass_timestamp, request_geonames

router = DefaultRouter(trailing_slash=False)
router.register(r'jobs', JobViewSet, base_name='jobs')
router.register(r'runs', ExportRunViewSet, base_name='runs')
router.register(
    r'configurations', ConfigurationViewSet, base_name='configurations')
router.register(
    r'hdx_export_regions',
    HDXExportRegionViewSet,
    base_name='hdx_export_regions')

urlpatterns = router.urls

urlpatterns += [
    url(r'^request_geonames$', login_required(request_geonames)),
    url(r'^overpass_timestamp$', login_required(get_overpass_timestamp)),
]
