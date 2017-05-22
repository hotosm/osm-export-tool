# -*- coding: utf-8 -*-
"""API url configuration."""

from rest_framework.routers import DefaultRouter

from api.views import (
    ExportFormatViewSet, ExportRunViewSet,
    ExportTaskViewSet, JobViewSet,
    HDXExportRegionViewSet
)

router = DefaultRouter(trailing_slash=False)
router.register(r'jobs', JobViewSet, base_name='jobs')
router.register(r'formats', ExportFormatViewSet, base_name='formats')
router.register(r'runs', ExportRunViewSet, base_name='runs')
router.register(r'tasks', ExportTaskViewSet, base_name='tasks')
router.register(r'hdx_export_regions', HDXExportRegionViewSet, base_name='hdx_export_regions')
