# -*- coding: utf-8 -*-
"""
HOT Export Tool URL Configuration
"""
from api.urls import router
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views.i18n import JavaScriptCatalog
from ui.views import (authorized, create_error_view, login, logout,
                      redirect_to_v3, v3)

urlpatterns = []

urlpatterns += i18n_patterns(
    url(r'^$', redirect_to_v3, name='index'),
    url(r'^v3/', v3, name="v3"),
    url(r'^login/$', login, name="login"),
    url(r'^logout$', logout, name='logout'),
    url(r'^error$', create_error_view, name='error'),
    url(r'^email/$', TemplateView.as_view(template_name='osm/email.html'),
        name='require_email'),
)

urlpatterns += [
    url(r'^authorized', authorized, name="authorized"),
]

urlpatterns += i18n_patterns(
    url(r'^admin/', include(admin.site.urls)),
)

# OAuth client urls
urlpatterns += i18n_patterns(
    url('^osm/', include('social_django.urls', namespace='osm')),
    url('^osm/email_verify_sent/$', TemplateView.as_view(
        template_name='osm/email_verify_sent.html'), name='email_verify_sent'),
    url('^osm/error$', TemplateView.as_view(template_name='osm/error.html'),
        name='login_error')
)

# OAuth provider urls
urlpatterns += [
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
]

# don't apply i18n patterns here.. api uses Accept-Language header
urlpatterns += [
    url(r'^api/', include(router.urls, namespace='api')),
    url(r'^api/', include('rest_framework.urls', namespace='rest_framework')),
]

# i18n for js
js_info_dict = {
    'packages': ('hot_osm',),
}

urlpatterns += [
    url(r'^jsi18n/$', JavaScriptCatalog.as_view(packages=['hot_osm']), name='javascript-catalog'),
    url(r'^i18n/', include('django.conf.urls.i18n')),
]

# handler500 = 'ui.views.internal_error_view'

# handler404 = 'ui.views.not_found_error_view'

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
