from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView, RedirectView
from django.views.i18n import JavaScriptCatalog

from ui.views import (
    authorized,
    login,
    logout,
    redirect_to_v3,
    v3,
    worker_dashboard,
    auth_me,
    auth_status,
    onboarding_callback,
)

# Hanko admin mapping routes
admin_mapping_patterns = []
if getattr(settings, 'AUTH_PROVIDER', 'legacy') == 'hanko':
    try:
        from hotosm_auth_django.admin_routes import create_admin_urlpatterns
        admin_mapping_patterns = create_admin_urlpatterns(
            app_name="osm-export-tool",
            user_model="auth.User",  # Django's built-in User model
            user_id_column="id",
            user_name_column="username",
            user_email_column="email",
        )
    except ImportError:
        pass

urlpatterns = [
    path("worker-dashboard/", worker_dashboard, name="worker_dashboard"),
    path("login/", login, name="login"),
    path("logout/", logout, name="logout"),
    path("api/auth/me/", auth_me, name="auth_me"),
    # Hanko auth endpoints (v1 convention matches Login service)
    path("api/v1/auth/status/", auth_status, name="auth_status"),
    path("api/v1/auth/onboarding/", onboarding_callback, name="onboarding_callback"),
    path("admin/login/", RedirectView.as_view(pattern_name="login", permanent=False)),
    path("admin/", admin.site.urls),
    path("api/", include("api.urls", namespace="api")),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("api/admin/", include(admin_mapping_patterns)),  # Hanko admin mappings
    path(
        "jsi18n/",
        JavaScriptCatalog.as_view(packages=["hot_osm"]),
        name="javascript-catalog",
    ),
    path("i18n/", include("django.conf.urls.i18n")),
    path("v3/", v3, name="v3"),
    path("", redirect_to_v3, name="index"),
]

# Legacy OAuth routes - only include when not using Hanko
if getattr(settings, 'AUTH_PROVIDER', 'legacy') != 'hanko':
    urlpatterns += [
        path(
            "email/",
            TemplateView.as_view(template_name="osm/email.html"),
            name="require_email",
        ),
        re_path(r"^authorized", authorized, name="authorized"),
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
    ]

# Catch-all route for React app
urlpatterns += [
    re_path(r"^(?!(o/|osm/|admin|api|worker)).*$", v3),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
