# -*- coding: utf-8 -*-
"""UI view definitions."""

from django.contrib.auth import logout as auth_logout
from django.urls import reverse
from django.shortcuts import redirect, render
from oauth2_provider.models import Application
from django.contrib import admin
from django.contrib.auth.admin import User, UserAdmin
from django.conf import settings
from django.http import (
    JsonResponse,
    HttpResponseRedirect,
    HttpResponse,
    HttpResponseNotFound,
    HttpResponseForbidden,
)
from django.views.decorators.http import require_http_methods

from .hanko_helpers import is_hanko_authenticated, get_mapped_django_user


def authorized(request):
    # the user has now authorized a client application; they no longer need to
    # be logged into the site (and it will be confusing if they are, since
    # "logging out" of the UI just drops the auth token)
    auth_logout(request)
    return v3(request)


def login(request):
    """
    Handle login - redirects to Hanko or OSM OAuth2 based on AUTH_PROVIDER.
    """
    # Check for Hanko authentication
    if getattr(settings, 'AUTH_PROVIDER', 'legacy') == 'hanko':
        if is_hanko_authenticated(request):
            return redirect("/v3/")
        # Redirect to Hanko login with return URL
        hanko_url = getattr(settings, 'HANKO_PUBLIC_URL', '')
        next_url = request.GET.get('next', '/v3/')
        return redirect(f"{hanko_url}/app?return_to={request.build_absolute_uri(next_url)}")

    # Legacy OSM OAuth2 authentication
    if not request.user.is_authenticated:
        # preserve redirects ("next" in request.GET)
        return redirect(
            reverse("osm:begin", args=["openstreetmap-oauth2"])
            + "?"
            + request.GET.urlencode()
        )
    else:
        return redirect("/v3/")


def logout(request):
    """Logs out user"""
    auth_logout(request)
    return redirect("/v3/")


def v3(request, *args, **kwargs):
    try:
        ui_app = Application.objects.get(name="OSM Export Tool UI")
    except Application.DoesNotExist:
        ui_app = Application.objects.create(
            name="OSM Export Tool UI",
            redirect_uris="http://localhost/authorized http://127.0.0.1:8000/authorized http://localhost:8080/authorized http://localhost:8000/authorized",
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_IMPLICIT,
            skip_authorization=True,
        )

    context = dict(
        client_id=ui_app.client_id,
        RAW_DATA_API_URL=settings.RAW_DATA_API_URL,
        AUTH_PROVIDER=getattr(settings, 'AUTH_PROVIDER', 'legacy'),
    )

    # Add Hanko public URL when using Hanko authentication
    if getattr(settings, 'AUTH_PROVIDER', 'legacy') == 'hanko':
        context['HANKO_PUBLIC_URL'] = getattr(settings, 'HANKO_PUBLIC_URL', '')

    if settings.MATOMO_URL is not None and settings.MATOMO_SITEID is not None:
        context.update(
            {"MATOMO_URL": settings.MATOMO_URL, "MATOMO_SITEID": settings.MATOMO_SITEID}
        )
    return render(request, "ui/v3.html", context)


def redirect_to_v3(request):
    return redirect("/v3/")


@require_http_methods(["GET"])
def worker_dashboard(request):
    # Check for superuser access based on auth provider
    if getattr(settings, 'AUTH_PROVIDER', 'legacy') == 'hanko':
        if not is_hanko_authenticated(request):
            return HttpResponseForbidden()
        admin_emails = getattr(settings, 'ADMIN_EMAILS', '').split(',')
        admin_emails = [email.strip() for email in admin_emails if email.strip()]
        if request.hotosm.user.email not in admin_emails:
            return HttpResponseForbidden()
    else:
        if not request.user.is_superuser:
            return HttpResponseForbidden()
    return HttpResponseRedirect(f"/{settings.WORKER_SECRET_KEY}/")


class ApplicationAdmin(admin.ModelAdmin):
    raw_id_fields = ("user",)


admin.site.register(Application, ApplicationAdmin)


# Hanko-specific views
@require_http_methods(["GET"])
def auth_me(request):
    """
    Get current user information.
    Works with both legacy and Hanko authentication.
    """
    if getattr(settings, 'AUTH_PROVIDER', 'legacy') == 'hanko':
        # Hanko authentication
        if not is_hanko_authenticated(request):
            return JsonResponse(
                {"error": "Not authenticated"},
                status=401
            )

        hanko_user = request.hotosm.user

        # Get or create mapped Django user
        django_user = get_mapped_django_user(request)

        response_data = {
            "hanko_user_id": hanko_user.id,
            "email": hanko_user.email,
            "auth_provider": "hanko",
        }

        # Add mapped Django user info
        if django_user:
            response_data.update({
                "user_id": django_user.id,
                "username": django_user.username,
            })

        # Add OSM connection info if available
        if hasattr(request.hotosm, 'osm') and request.hotosm.osm:
            osm = request.hotosm.osm
            response_data.update({
                "osm_username": osm.osm_username,
                "osm_user_id": osm.osm_user_id,
            })

        return JsonResponse(response_data)
    else:
        # Legacy authentication
        if not request.user.is_authenticated:
            return JsonResponse(
                {"error": "Not authenticated"},
                status=401
            )

        return JsonResponse({
            "user_id": request.user.id,
            "username": request.user.username,
            "email": request.user.email,
            "auth_provider": "legacy",
        })


@require_http_methods(["GET"])
def auth_osm_status(request):
    """
    Check authentication and OSM connection status.
    Always returns 200 when Hanko-authenticated so the web component
    can parse the response (it only processes response.ok / 200-299).
    """
    if getattr(settings, 'AUTH_PROVIDER', 'legacy') != 'hanko':
        return JsonResponse({
            "auth_provider": "legacy",
            "authenticated": request.user.is_authenticated,
            "connected": True,
            "message": "Using legacy OSM OAuth2 authentication"
        })

    if not is_hanko_authenticated(request):
        return JsonResponse(
            {"auth_provider": "hanko", "authenticated": False},
            status=401
        )

    hanko_user = request.hotosm.user
    django_user = get_mapped_django_user(request)

    response_data = {
        "auth_provider": "hanko",
        "authenticated": True,
        "hanko_user": {
            "id": hanko_user.id,
            "email": hanko_user.email,
        },
    }

    if django_user:
        response_data["user"] = {
            "id": django_user.id,
            "username": django_user.username,
        }

    if hasattr(request.hotosm, 'osm') and request.hotosm.osm:
        osm = request.hotosm.osm
        response_data["connected"] = True
        response_data["osm_username"] = osm.osm_username
        response_data["osm_user_id"] = osm.osm_user_id
    else:
        response_data["connected"] = False

    return JsonResponse(response_data)
