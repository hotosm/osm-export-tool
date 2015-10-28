# -*- coding: utf-8 -*-
from rest_framework.renderers import BrowsableAPIRenderer


class HOTExportApiRenderer(BrowsableAPIRenderer):
    """Custom APIRenderer to remove editing forms from Browsable API."""

    def get_context(self, data, accepted_media_type, renderer_context):
        context = super(HOTExportApiRenderer, self).get_context(data, accepted_media_type, renderer_context)
        context['display_edit_forms'] = False
        return context
