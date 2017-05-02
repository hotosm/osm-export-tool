# -*- coding: utf-8 -*-
"""UI view definitions."""

from cachetools.func import ttl_cache

import dateutil.parser

from django.conf import settings
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

import requests


@ttl_cache(ttl=60)
def get_overpass_last_updated_at():
    r = requests.get('{}timestamp'.format(settings.OVERPASS_API_URL))

    return dateutil.parser.parse(r.content)


@require_http_methods(['GET'])
def create_export(request):
    """
    Handle display of the create export page.
    """
    return render(request, 'ui/create.html', {
        'max_extent': settings.JOB_MAX_EXTENT,
        'overpass_last_updated_at': get_overpass_last_updated_at(),
    })


@require_http_methods(['GET'])
def clone_export(request, uuid=None):
    """
    Handle display of the clone export page.
    """
    return render(request, 'ui/clone.html', {
        'max_extent': settings.JOB_MAX_EXTENT,
        'overpass_last_updated_at': get_overpass_last_updated_at(),
    })


def login(request):
    exports_url = reverse('list')
    help_url = reverse('help')
    if not request.user.is_authenticated():
        return render(request, 'osm/login.html', {
            'exports_url': exports_url,
            'help_url': help_url
        })
    else:
        return redirect('create')


def logout(request):
    """Logs out user"""
    exports_url = reverse('list')
    help_url = reverse('help')
    auth_logout(request)
    return render(request, 'osm/login.html', {
        'exports_url': exports_url,
        'help_url': help_url
    })


@permission_required((
    'jobs.add_hdxexportregion',
    'jobs.change_hdxexportregion',
    'jobs.delete_hdxexportregion',
))
def hdx_list(request):
    return render(request, 'ui/base_react.html')


def require_email(request):
    """
    View to handle email collection for new user logging in with OSM account.
    """
    backend = request.session['partial_pipeline']['backend']
    return render(request, 'osm/email.html', {
        'backend': backend
    })


@require_http_methods(['GET'])
def about(request):
    exports_url = reverse('list')
    help_url = reverse('help')
    return render(request, 'ui/about.html', {
        'exports_url': exports_url,
        'help_url': help_url
    })


@require_http_methods(['GET'])
def help_main(request):
    return render(request, 'help/help.html')


@require_http_methods(['GET'])
def help_create(request):
    create_url = reverse('create')
    help_features_url = reverse('help_features')
    return render(request, 'help/help_create.html', {
        'create_url': create_url,
        'help_features_url': help_features_url
    })


@require_http_methods(['GET'])
def help_features(request):
    return render(request, 'help/help_features.html')

@require_http_methods(['GET'])
def help_feature_selections(request):
    return render(request, 'help/help_feature_selections.html')


@require_http_methods(['GET'])
def help_exports(request):
    help_main_url = reverse('help')
    export_url = reverse('list')
    return render(request, 'help/help_exports.html', {
        'export_url': export_url
    })


@require_http_methods(['GET'])
def help_formats(request):
    return render(request, 'help/help_formats.html')


@require_http_methods(['GET'])
def help_presets(request):
    configurations_url = reverse('configurations')
    return render(request, 'help/help_presets.html', {
        'configurations_url': configurations_url
    })

# error views


@require_http_methods(['GET'])
def create_error_view(request):
    return render(request, 'ui/error.html', status=500)


def internal_error_view(request):
    return render(request, 'ui/500.html', status=500)


def not_found_error_view(request):
    return render(request, 'ui/404.html', status=404)


def not_allowed_error_view(request):
    return render(request, 'ui/403.html', status=403)
