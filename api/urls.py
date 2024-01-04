from django.urls import re_path, path
from rest_framework.routers import DefaultRouter
from .views import (
    ConfigurationViewSet,
    ExportRunViewSet,
    HDXExportRegionViewSet,
    PartnerExportRegionViewSet,
    JobViewSet,
    permalink,
    get_overpass_timestamp,
    cancel_run,
    get_user_permissions,
    request_geonames,
    get_overpass_status,
    get_groups,
    stats,
    run_stats,
    request_nominatim,
    machine_status,
)

router = DefaultRouter(trailing_slash=False)
router.register(r"jobs", JobViewSet, basename="jobs")
router.register(r"runs", ExportRunViewSet, basename="runs")
router.register(r"configurations", ConfigurationViewSet, basename="configurations")
router.register(
    r"hdx_export_regions", HDXExportRegionViewSet, basename="hdx_export_regions"
)
router.register(
    r"partner_export_regions",
    PartnerExportRegionViewSet,
    basename="partner_export_regions",
)

app_name = "api"
urlpatterns = router.urls + [
    re_path(r"^permalink/(?P<uid>[a-z0-9\-]+)$", permalink),
    path("request_nominatim", request_nominatim),
    path("request_geonames", request_geonames),
    path("overpass_timestamp", get_overpass_timestamp),
    path("overpass_status", get_overpass_status),
    path("permissions", get_user_permissions),
    path("groups", get_groups),
    path("stats", stats),
    path("run_stats", run_stats),
    path("status", machine_status),
    path("cancel_run", cancel_run),
]
