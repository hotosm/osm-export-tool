# -*- coding: utf-8 -*-
"""API url configuration."""

from rest_framework.routers import DefaultRouter

from api.views import (
    ExportConfigViewSet, ExportFormatViewSet, ExportRunViewSet,
    ExportTaskViewSet, JobViewSet, PresetViewSet,
    HDXExportRegionViewSet
)

router = DefaultRouter(trailing_slash=False)
router.register(r'jobs', JobViewSet, base_name='jobs')
router.register(r'formats', ExportFormatViewSet, base_name='formats')
router.register(r'runs', ExportRunViewSet, base_name='runs')
router.register(r'tasks', ExportTaskViewSet, base_name='tasks')
router.register(r'configurations', ExportConfigViewSet, base_name='configs')
router.register(r'configuration/presets', PresetViewSet, base_name='presets')
router.register(r'hdx_export_regions', HDXExportRegionViewSet, base_name='hdx_export_regions')
