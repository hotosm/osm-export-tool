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


def authorized(request):
    # the user has now authorized a client application; they no longer need to
    # be logged into the site (and it will be confusing if they are, since
    # "logging out" of the UI just drops the auth token)
    auth_logout(request)
    return render(request, "ui/authorized.html")


def login(request):
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
        client_id=ui_app.client_id, RAW_DATA_API_URL=settings.RAW_DATA_API_URL
    )
    if settings.MATOMO_URL is not None and settings.MATOMO_SITEID is not None:
        context.update(
            {"MATOMO_URL": settings.MATOMO_URL, "MATOMO_SITEID": settings.MATOMO_SITEID}
        )
    return render(request, "ui/v3.html", context)


def redirect_to_v3(request):
    return redirect("/v3/")


@require_http_methods(["GET"])
def worker_dashboard(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    return HttpResponseRedirect(f"/{settings.WORKER_SECRET_KEY}/")


class ApplicationAdmin(admin.ModelAdmin):
    raw_id_fields = ("user",)


admin.site.register(Application, ApplicationAdmin)
