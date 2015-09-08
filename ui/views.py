from django.shortcuts import render_to_response, RequestContext
from django.views.decorators.http import require_http_methods
from django.template.context_processors import csrf
from django.contrib.auth.models import Group


"""
 Handles display of the create export page.
"""
@require_http_methods(['GET'])
def create_export(request):
    user = request.user
    max_extent = {'extent': 2500000} # default
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