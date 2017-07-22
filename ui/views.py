# -*- coding: utf-8 -*-
"""UI view definitions."""

from django.conf import settings
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

def login(request):
    help_url = reverse('help')
    if not request.user.is_authenticated():
        return render(request, 'osm/login.html', {
            'help_url': help_url
        })
    else:
        return redirect('/v3/#/exports/new')


def logout(request):
    """Logs out user"""
    help_url = reverse('help')
    auth_logout(request)
    return render(request, 'osm/login.html', {
        'help_url': help_url
    })


def v3(request):
    return render(request, 'ui/v3.html')


def require_email(request):
    """
    View to handle email collection for new user logging in with OSM account.
    """
    return render(request, 'osm/email.html')


@require_http_methods(['GET'])
def about(request):
    help_url = reverse('help')
    return render(request, 'ui/about.html', {
        'help_url': help_url
    })


@require_http_methods(['GET'])
def help_main(request):
    return render(request, 'help/help.html')


@require_http_methods(['GET'])
def help_create(request):
    help_features_url = reverse('help_features')
    return render(request, 'help/help_create.html', {
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
    return render(request, 'help/help_exports.html')


@require_http_methods(['GET'])
def help_formats(request):
    return render(request, 'help/help_formats.html')


@require_http_methods(['GET'])
def help_presets(request):
    return render(request, 'help/help_presets.html')

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
