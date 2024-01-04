from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView, RedirectView
from django.views.i18n import JavaScriptCatalog

from ui.views import authorized, login, logout, redirect_to_v3, v3, worker_dashboard

urlpatterns = [
    path("", redirect_to_v3, name="index"),
    path("v3/", v3, name="v3"),
    re_path(r"^(?:.*)/?$", v3),
    path("worker-dashboard/", worker_dashboard, name="worker_dashboard"),
    path("login/", login, name="login"),
    path("logout/", logout, name="logout"),
    path(
        "email/",
        TemplateView.as_view(template_name="osm/email.html"),
        name="require_email",
    ),
    re_path(r"^authorized", authorized, name="authorized"),
    path("admin/login/", RedirectView.as_view(pattern_name="login", permanent=False)),
    path("admin/", admin.site.urls),
    path("osm/", include("social_django.urls", namespace="osm")),
    path(
        "osm/email_verify_sent/",
        TemplateView.as_view(template_name="osm/email_verify_sent.html"),
        name="email_verify_sent",
    ),
    path(
        "osm/error",
        TemplateView.as_view(template_name="osm/error.html"),
        name="login_error",
    ),
    path("o/", include("oauth2_provider.urls", namespace="oauth2_provider")),
    path("api/", include("api.urls", namespace="api")),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path(
        "jsi18n/",
        JavaScriptCatalog.as_view(packages=["hot_osm"]),
        name="javascript-catalog",
    ),
    path("i18n/", include("django.conf.urls.i18n")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
