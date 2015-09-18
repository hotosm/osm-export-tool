import oauth2 as oauth
import urlparse

from django.shortcuts import render_to_response, RequestContext
from django.views.decorators.http import require_http_methods
from django.template.context_processors import csrf
from django.contrib.auth.models import Group
from django.contrib.auth import logout as auth_logout
from social.backends.utils import load_backends
from social.apps.django_app.utils import psa
from django.conf import settings


"""
 Handles display of the create export page.
"""
@require_http_methods(['GET'])
def create_export(request):
    user = request.user
    max_extent = {'extent': settings.JOB_MAX_EXTENT}
    for group in user.groups.all():
        if hasattr(group, 'export_profile'):
            max_extent['extent'] = group.export_profile.max_extent
    extent = max_extent.get('extent')
    context = {'user': user, 'max_extent': extent}
    context.update(csrf(request))
    return render_to_response('ui/create.html', context)

"""
 Handles display of the clone export page.
"""
@require_http_methods(['GET'])
def clone_export(request, uuid=None):
    user = request.user
    max_extent = {'extent': 2500000} # default
    for group in user.groups.all():
        if hasattr(group, 'export_profile'):
            max_extent['extent'] = group.export_profile.max_extent
    extent = max_extent.get('extent')
    context = {'user': user, 'max_extent': extent}
    context.update(csrf(request))
    return render_to_response('ui/clone.html', context)


def logout(request):
    """Logs out user"""
    auth_logout(request)
    return render_to_response('osm/login.html', {}, RequestContext(request))


def require_email(request):
    backend = request.session['partial_pipeline']['backend']
    return render_to_response('osm/email.html', {'backend': backend}, RequestContext(request))

@require_http_methods(['GET'])
def create_error_view(request):
    return render_to_response('ui/error.html', {}, RequestContext(request))

def internal_error_view(request):
    return render_to_response('ui/500.html', {}, RequestContext(request))
