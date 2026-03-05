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

from .hanko_helpers import (
    is_hanko_authenticated,
    get_mapped_django_user,
    find_legacy_user_by_osm_id,
    find_legacy_user_by_email,
    create_export_tool_user,
    APP_NAME,
)



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
        RAW_DATA_API_URL=getattr(settings, 'RAW_DATA_API_PUBLIC_URL', settings.RAW_DATA_API_URL),
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
def auth_status(request):
    """
    Check authentication status for Hanko users.

    Returns:
    - authenticated: true if user has valid mapping
    - needs_onboarding: true if user needs to complete onboarding
    - hanko_user: Hanko user info if authenticated with Hanko

    This endpoint is used by the hotosm-auth web component's mapping-check-url.
    Only works when AUTH_PROVIDER=hanko.
    """
    from hotosm_auth_django import get_mapped_user_id

    # Only for Hanko auth
    if getattr(settings, 'AUTH_PROVIDER', 'legacy') != 'hanko':
        return JsonResponse({
            "auth_provider": "legacy",
            "authenticated": request.user.is_authenticated if hasattr(request, 'user') else False,
        })

    # Check Hanko user
    if not is_hanko_authenticated(request):
        return JsonResponse({
            "auth_provider": "hanko",
            "authenticated": False,
            "hanko_authenticated": False,
        })

    hanko_user = request.hotosm.user

    # Check mapping
    mapped_user_id = get_mapped_user_id(hanko_user, app_name=APP_NAME)

    if mapped_user_id is not None:
        # Has mapping - fully authenticated
        try:
            django_user_id = int(mapped_user_id)
            user = User.objects.get(id=django_user_id)
            return JsonResponse({
                "auth_provider": "hanko",
                "authenticated": True,
                "needs_onboarding": False,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
                "hanko_user": {
                    "id": hanko_user.id,
                    "email": hanko_user.email,
                }
            })
        except User.DoesNotExist:
            pass  # Fall through to needs_onboarding

    # No mapping - needs onboarding
    return JsonResponse({
        "auth_provider": "hanko",
        "authenticated": False,
        "needs_onboarding": True,
        "hanko_authenticated": True,
        "hanko_user": {
            "id": hanko_user.id,
            "email": hanko_user.email,
        }
    })


@require_http_methods(["GET"])
def onboarding_callback(request):
    """
    Handle onboarding callback from login service.

    This endpoint is called after the user completes onboarding in login.hotosm.org.
    It creates the Django User and mapping based on whether the user is new or legacy.

    Query params:
    - new_user=true: User is new, create new Django user
    - (no param): User is legacy, osm_connection cookie should be set

    Only works when AUTH_PROVIDER=hanko.
    """
    from hotosm_auth_django import create_user_mapping

    # Only for Hanko auth
    if getattr(settings, 'AUTH_PROVIDER', 'legacy') != 'hanko':
        return JsonResponse(
            {"error": "Onboarding only available with Hanko auth"},
            status=400
        )

    # Need Hanko user from middleware
    if not is_hanko_authenticated(request):
        return JsonResponse(
            {"error": "Not authenticated with Hanko"},
            status=401
        )

    hanko_user = request.hotosm.user
    is_new_user = request.GET.get('new_user') == 'true'

    if is_new_user:
        # New user - create Django user with email as username base
        username = hanko_user.email.split('@')[0]

        # Create User
        user = create_export_tool_user(
            username=username,
            email=hanko_user.email,
        )

        # Create mapping
        create_user_mapping(
            hanko_user_id=hanko_user.id,
            app_user_id=str(user.id),
            app_name=APP_NAME,
        )

        # Redirect to export tool homepage
        return HttpResponseRedirect("/v3/")

    else:
        # Legacy user - should have osm_connection cookie
        osm_connection = getattr(request.hotosm, 'osm', None)

        if not osm_connection:
            from urllib.parse import urlencode
            login_url = getattr(settings, 'HANKO_PUBLIC_URL', '') or getattr(settings, 'HANKO_API_URL', 'https://login.hotosm.org')
            params = urlencode({
                'onboarding': 'osm-export-tool',
                'return_to': request.build_absolute_uri('/v3/'),
                'error': 'OSM connection failed. Please try connecting your OSM account again.',
            })
            return HttpResponseRedirect(f"{login_url}/app?{params}")

        osm_id = osm_connection.osm_user_id
        osm_username = osm_connection.osm_username

        # Check if User already exists (true legacy)
        # Priority: 1) OSM ID (via social_auth), 2) Email (Hanko email)
        existing_user = find_legacy_user_by_osm_id(osm_id) if osm_id else None
        if not existing_user:
            # Fallback to email - use Hanko user's email
            existing_user = find_legacy_user_by_email(hanko_user.email)

        if not existing_user:
            # No existing export tool account with this OSM ID or email
            # Redirect back to Login with error message
            from urllib.parse import urlencode
            login_url = getattr(settings, 'HANKO_PUBLIC_URL', '') or getattr(settings, 'HANKO_API_URL', 'https://login.hotosm.org')
            error_msg = f"No existing account found for OSM user '{osm_username}' (osm_id={osm_id}). Please select 'No, I'm new' to create a new account."
            params = urlencode({
                'onboarding': 'osm-export-tool',
                'return_to': request.build_absolute_uri('/v3/'),
                'error': error_msg,
            })
            return HttpResponseRedirect(f"{login_url}/app?{params}")

        # True legacy user - create mapping
        create_user_mapping(
            hanko_user_id=hanko_user.id,
            app_user_id=str(existing_user.id),
            app_name=APP_NAME,
        )

        # Redirect to export tool homepage
        return HttpResponseRedirect("/v3/")
