# -*- coding: utf-8 -*-
"""UI view definitions."""

from cachetools.func import ttl_cache

import dateutil.parser

from django.conf import settings
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.shortcuts import RequestContext, redirect, render_to_response
from django.template.context_processors import csrf
from django.views.decorators.http import require_http_methods

import requests


@ttl_cache(ttl=60)
def get_overpass_last_updated_at():
    r = requests.get('{}?data=[out:json];out;'.format(settings.OVERPASS_API_URL)).json()

    return dateutil.parser.parse(r['osm3s']['timestamp_osm_base'])


@require_http_methods(['GET'])
def create_export(request):
    """
    Handles display of the create export page.
    """
    user = request.user
    max_extent = {'extent': settings.JOB_MAX_EXTENT}
    extent = max_extent.get('extent')
    context = {
        'user': user,
        'max_extent': extent,
        'overpass_last_updated_at': get_overpass_last_updated_at(),
    }
    context.update(csrf(request))
    return render_to_response('ui/create.html', context)


@require_http_methods(['GET'])
def clone_export(request, uuid=None):
    """
    Handles display of the clone export page.
    """
    user = request.user
    max_extent = {'extent': settings.JOB_MAX_EXTENT}  # default
    extent = max_extent.get('extent')
    context = {
        'user': user,
        'max_extent': extent,
        'overpass_last_updated_at': get_overpass_last_updated_at(),
    }
    context.update(csrf(request))
    return render_to_response('ui/clone.html', context)


def login(request):
    exports_url = reverse('list')
    help_url = reverse('help')
    if not request.user.is_authenticated():
        return render_to_response(
            'osm/login.html',
            {'exports_url': exports_url, 'help_url': help_url},
            RequestContext(request)
        )
    else:
        return redirect('create')


def logout(request):
    """Logs out user"""
    exports_url = reverse('list')
    help_url = reverse('help')
    auth_logout(request)
    return render_to_response(
        'osm/login.html',
        {'exports_url': exports_url, 'help_url': help_url},
        RequestContext(request)
    )


@permission_required((
    'jobs.add_hdxexportregion',
    'jobs.change_hdxexportregion',
    'jobs.delete_hdxexportregion',
))
def hdx_list(request):
    user = request.user
    context = {
        'user': user,
        'reactRootClass': 'rootHdxList'
    }
    return render_to_response('ui/base_react.html', context)


def require_email(request):
    """
    View to handle email collection for new user logging in with OSM account.
    """
    backend = request.session['partial_pipeline']['backend']
    return render_to_response('osm/email.html', {'backend': backend}, RequestContext(request))


@require_http_methods(['GET'])
def about(request):
    exports_url = reverse('list')
    help_url = reverse('help')
    return render_to_response(
        'ui/about.html',
        {'exports_url': exports_url, 'help_url': help_url},
        RequestContext(request)
    )


@require_http_methods(['GET'])
def help_main(request):
    return render_to_response('help/help.html', {}, RequestContext(request))


@require_http_methods(['GET'])
def help_create(request):
    create_url = reverse('create')
    help_features_url = reverse('help_features')
    return render_to_response(
        'help/help_create.html',
        {'create_url': create_url, 'help_features_url': help_features_url},
        RequestContext(request)
    )


@require_http_methods(['GET'])
def help_features(request):
    return render_to_response(
        'help/help_features.html', {}, RequestContext(request)
    )


@require_http_methods(['GET'])
def help_exports(request):
    help_main_url = reverse('help')
    export_url = reverse('list')
    return render_to_response(
        'help/help_exports.html', {'export_url': export_url}, RequestContext(request)
    )


@require_http_methods(['GET'])
def help_formats(request):
    return render_to_response(
        'help/help_formats.html', {}, RequestContext(request)
    )


@require_http_methods(['GET'])
def help_presets(request):
    configurations_url = reverse('configurations')
    return render_to_response(
        'help/help_presets.html',
        {'configurations_url': configurations_url},
        RequestContext(request)
    )

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
