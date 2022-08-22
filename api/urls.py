# -*- coding: utf-8 -*-
"""API url configuration."""

from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from .views import (ConfigurationViewSet, ExportRunViewSet,
                    HDXExportRegionViewSet, PartnerExportRegionViewSet, JobViewSet, permalink, get_overpass_timestamp,
                    get_user_permissions, request_geonames, get_overpass_status, get_groups, stats, request_nominatim,status)

router = DefaultRouter(trailing_slash=False)
router.register(r'jobs', JobViewSet, base_name='jobs')
router.register(r'runs', ExportRunViewSet, base_name='runs')
router.register(
    r'configurations', ConfigurationViewSet, base_name='configurations')
router.register(
    r'hdx_export_regions',
    HDXExportRegionViewSet,
    base_name='hdx_export_regions')
router.register(
    r'partner_export_regions',
    PartnerExportRegionViewSet,
    base_name='partner_export_regions')


urlpatterns = router.urls

urlpatterns += [
    url(r'^permalink/(?P<uid>[a-z0-9\-]+)$', permalink),
    url(r'^request_nominatim$', request_nominatim),
    url(r'^request_geonames$', request_geonames),
    url(r'^overpass_timestamp$', get_overpass_timestamp),
    url(r'^overpass_status$', get_overpass_status),
    url(r'^permissions$', get_user_permissions),
    url(r'^groups$',get_groups),
    url(r'^stats$', stats),
    url(r'^status$', status),
    
]
