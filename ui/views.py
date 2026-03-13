from django.contrib.auth import logout as auth_logout
from django.db import IntegrityError
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
    if getattr(settings, 'AUTH_PROVIDER', 'legacy') == 'hanko':
        if is_hanko_authenticated(request):
            return redirect("/v3/")
        hanko_url = getattr(settings, 'HANKO_PUBLIC_URL', '')
        next_url = request.GET.get('next', '/v3/')
        return redirect(f"{hanko_url}/app?return_to={request.build_absolute_uri(next_url)}")

    if not request.user.is_authenticated:
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


@require_http_methods(["GET"])
def auth_me(request):
    if is_hanko_authenticated(request):
        django_user = get_mapped_django_user(request)
        if not django_user:
            return JsonResponse({"error": "Not authenticated"}, status=401)

        response_data = {
            "user_id": django_user.id,
            "username": django_user.username,
            "email": django_user.email,
        }

        if hasattr(request.hotosm, 'osm') and request.hotosm.osm:
            osm = request.hotosm.osm
            response_data.update({
                "osm_username": osm.osm_username,
                "osm_user_id": osm.osm_user_id,
            })

        return JsonResponse(response_data)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)

    return JsonResponse({
        "user_id": request.user.id,
        "username": request.user.username,
        "email": request.user.email,
    })


@require_http_methods(["GET"])
def auth_status(request):
    from hotosm_auth_django import get_mapped_user_id

    if not is_hanko_authenticated(request):
        return JsonResponse({
            "authenticated": request.user.is_authenticated if hasattr(request, 'user') else False,
            "hanko_authenticated": False,
            "needs_onboarding": False,
        })

    hanko_user = request.hotosm.user
    mapped_user_id = get_mapped_user_id(hanko_user, app_name=APP_NAME)

    if mapped_user_id is not None:
        try:
            user = User.objects.get(id=int(mapped_user_id))
            return JsonResponse({
                "authenticated": True,
                "hanko_authenticated": True,
                "needs_onboarding": False,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
            })
        except User.DoesNotExist:
            pass

    return JsonResponse({
        "authenticated": False,
        "hanko_authenticated": True,
        "needs_onboarding": True,
        "hanko_user": {
            "id": hanko_user.id,
            "email": hanko_user.email,
        },
    })


@require_http_methods(["GET"])
def onboarding_callback(request):
    from hotosm_auth_django import create_user_mapping, get_mapped_user_id
    from urllib.parse import urlencode

    if getattr(settings, 'AUTH_PROVIDER', 'legacy') != 'hanko':
        return JsonResponse(
            {"error": "Onboarding only available with Hanko auth"},
            status=400
        )

    if not is_hanko_authenticated(request):
        return JsonResponse(
            {"error": "Not authenticated with Hanko"},
            status=401
        )

    hanko_user = request.hotosm.user
    is_new_user = request.GET.get('new_user') == 'true'
    login_url = getattr(settings, 'HANKO_PUBLIC_URL', '') or getattr(settings, 'HANKO_API_URL', 'https://login.hotosm.org')

    if is_new_user:
        # If a valid mapping already exists, skip creation and go home
        existing_mapped_id = get_mapped_user_id(hanko_user, app_name=APP_NAME)
        if existing_mapped_id:
            try:
                User.objects.get(id=int(existing_mapped_id))
                return HttpResponseRedirect("/v3/")
            except (User.DoesNotExist, ValueError):
                # Stale mapping — fall through to re-create
                pass

        # If user already has an OSM connection, check for an existing account
        # (avoids creating a duplicate when user connected OSM but chose "new")
        osm_connection = getattr(request.hotosm, 'osm', None)
        if osm_connection and osm_connection.osm_user_id:
            existing_by_osm = find_legacy_user_by_osm_id(osm_connection.osm_user_id)
            if existing_by_osm:
                try:
                    create_user_mapping(
                        hanko_user_id=hanko_user.id,
                        app_user_id=str(existing_by_osm.id),
                        app_name=APP_NAME,
                    )
                except IntegrityError:
                    pass  # Mapping already exists, that's fine
                return HttpResponseRedirect("/v3/")

        # Truly new user - create Django user with email as username base
        user = create_export_tool_user(
            username=hanko_user.email.split('@')[0],
            email=hanko_user.email,
        )

        try:
            create_user_mapping(
                hanko_user_id=hanko_user.id,
                app_user_id=str(user.id),
                app_name=APP_NAME,
            )
        except IntegrityError:
            pass  # Race condition or duplicate call, mapping already exists

        return HttpResponseRedirect("/v3/")

    else:
        # Legacy user - need OSM connection cookie to look up their account
        osm_connection = getattr(request.hotosm, 'osm', None)

        if not osm_connection:
            from hotosm_auth_django import get_auth_config
            config = get_auth_config()
            if config.osm_enabled:
                # OSM credentials configured locally — initiate OAuth on this app so
                # the cookie is set with our own COOKIE_SECRET.
                return HttpResponseRedirect('/api/v1/auth/osm/login/')
            else:
                # No local OSM credentials — send back to Login service to connect OSM.
                # Requires COOKIE_SECRET to be shared between Login service and this app.
                params = urlencode({
                    'onboarding': APP_NAME,
                    'return_to': request.build_absolute_uri('/v3/'),
                    'error': 'OSM connection required. Please connect your OSM account.',
                })
                return HttpResponseRedirect(f"{login_url}/app?{params}")

        osm_id = osm_connection.osm_user_id

        # Check if User already exists (true legacy)
        # Priority: 1) OSM ID (via social_auth), 2) Email (Hanko email)
        existing_user = find_legacy_user_by_osm_id(osm_id) if osm_id else None
        if not existing_user:
            existing_user = find_legacy_user_by_email(hanko_user.email)

        if not existing_user:
            # No existing export tool account with this OSM ID or email
            error_msg = "No existing account found for your OSM user. Please select 'No, I\u2019m new' to create a new account."
            params = urlencode({
                'onboarding': APP_NAME,
                'return_to': request.build_absolute_uri('/v3/'),
                'error': error_msg,
            })
            return HttpResponseRedirect(f"{login_url}/app?{params}")

        # True legacy user - create mapping
        try:
            create_user_mapping(
                hanko_user_id=hanko_user.id,
                app_user_id=str(existing_user.id),
                app_name=APP_NAME,
            )
        except IntegrityError:
            pass  # Mapping already exists (duplicate call), that's fine

        return HttpResponseRedirect("/v3/")
