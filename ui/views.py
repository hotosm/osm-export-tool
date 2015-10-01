# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.auth import logout as auth_logout
from django.shortcuts import RequestContext, redirect, render_to_response
from django.template.context_processors import csrf
from django.views.decorators.http import require_http_methods


@require_http_methods(['GET'])
def create_export(request):
    """
    Handles display of the create export page.
    """
    user = request.user
    max_extent = {'extent': settings.JOB_MAX_EXTENT}
    for group in user.groups.all():
        if hasattr(group, 'export_profile'):
            max_extent['extent'] = group.export_profile.max_extent
    extent = max_extent.get('extent')
    context = {'user': user, 'max_extent': extent}
    context.update(csrf(request))
    return render_to_response('ui/create.html', context)


@require_http_methods(['GET'])
def clone_export(request, uuid=None):
    """
    Handles display of the clone export page.
    """
    user = request.user
    max_extent = {'extent': settings.JOB_MAX_EXTENT}  # default
    for group in user.groups.all():
        if hasattr(group, 'export_profile'):
            max_extent['extent'] = group.export_profile.max_extent
    extent = max_extent.get('extent')
    context = {'user': user, 'max_extent': extent}
    context.update(csrf(request))
    return render_to_response('ui/clone.html', context)


def login(request):
    if not request.user.is_authenticated():
        return render_to_response('osm/login.html', {}, RequestContext(request))
    else:
        return redirect('create')


def logout(request):
    """Logs out user"""
    auth_logout(request)
    return render_to_response('osm/login.html', {}, RequestContext(request))


def require_email(request):
    """
    View to handle email collection for new user loging in with OSM account.
    """
    backend = request.session['partial_pipeline']['backend']
    return render_to_response('osm/email.html', {'backend': backend}, RequestContext(request))

# error views


@require_http_methods(['GET'])
def create_error_view(request):
    return render_to_response('ui/error.html', {}, RequestContext(request), status=500)


def internal_error_view(request):
    return render_to_response('ui/500.html', {}, RequestContext(request), status=500)


def not_found_error_view(request):
    return render_to_response('ui/404.html', {}, RequestContext(request), status=404)


def not_allowed_error_view(request):
    return render_to_response('ui/403.html', {}, RequestContext(request), status=403)
