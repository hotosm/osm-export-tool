"""
    API url configuration
"""
from api.views import (JobViewSet, ExportFormatViewSet,
                       RegionViewSet, RegionMaskViewSet, ExportRunViewSet)
from rest_framework.routers import DefaultRouter

router = DefaultRouter(trailing_slash=False)
router.register(r'jobs', JobViewSet, base_name='jobs')
router.register(r'formats', ExportFormatViewSet, base_name='formats')
router.register(r'runs', ExportRunViewSet, base_name='runs')
router.register(r'regions', RegionViewSet, base_name='regions')
router.register(r'maskregions', RegionMaskViewSet, base_name='mask')


