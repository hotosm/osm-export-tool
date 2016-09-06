# -*- coding: utf-8 -*-
from __future__ import absolute_import

from .base import *  # NOQA

# Extra installed apps
INSTALLED_APPS += (
    # any 3rd party apps
    'rest_framework',
    'rest_framework_gis',
    'rest_framework.authtoken',
    'social.apps.django_app.default'
)

# 3rd party specific app settings


REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',
                                'rest_framework.filters.SearchFilter',
                                'rest_framework.filters.OrderingFilter'),
    'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework.authentication.SessionAuthentication',
                                       'rest_framework.authentication.TokenAuthentication'),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'oet2.api.renderers.HOTExportApiRenderer',
    ),
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.AcceptHeaderVersioning',
    'DEFAULT_VERSION': '1.0',
}

# OAuth login settings
SOCIAL_AUTH_OPENSTREETMAP_LOGIN_URL = '/osm/login/'
SOCIAL_AUTH_OPENSTREETMAP_KEY = '56e4WINtKE9BSzIU1JtYZufLRBp0La5zS6qHvei3'
SOCIAL_AUTH_OPENSTREETMAP_SECRET = 'fcwFW11HB3zFDUQonYUTS3QJEQ5IAowWmISu2l93'
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/exports/create/'
SOCIAL_AUTH_LOGIN_ERROR_URL = '/osm/error'
SOCIAL_AUTH_URL_NAMESPACE = 'osm'
SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS = ['username', 'first_name', 'email']
SOCIAL_AUTH_FORCE_EMAIL_VALIDATION = True
SOCIAL_AUTH_EMAIL_VALIDATION_FUNCTION = 'oet2.ui.pipeline.email_validation'
SOCIAL_AUTH_EMAIL_VALIDATION_URL = '/osm/email_verify_sent/'

# SOCIAL_AUTH_STRATEGY = 'social.strategies.django_strategy.DjangoStrategy'
# SOCIAL_AUTH_STORAGE = 'social.apps.django_app.default.models.DjangoStorage'

SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'social.pipeline.user.get_username',
    'oet2.ui.pipeline.require_email',
    'social.pipeline.mail.mail_validation',
    'social.pipeline.social_auth.associate_by_email',
    'social.pipeline.user.create_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.debug.debug',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details'
)
