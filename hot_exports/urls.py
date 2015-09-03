"""
HOT Exports URL Configuration
"""
from django.conf.urls import include, url, patterns
from django.conf.urls.i18n import i18n_patterns
from django.contrib.auth.decorators import login_required
from django.contrib import admin
from django.contrib import auth
from ui import urls as ui_urls
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from api.urls import router
from api.views import HDMDataModelView, OSMDataModelView, RunJob

urlpatterns = []

urlpatterns += i18n_patterns('ui.views',
    url(r'^$', login_required(TemplateView.as_view(template_name='ui/index.html')), name='index'),
    url(r'^jobs/', include(ui_urls)),
)

urlpatterns += i18n_patterns('ui.help',
    url(r'^about$', TemplateView.as_view(template_name='ui/about.html'), name='about'),
    url(r'^help$', TemplateView.as_view(template_name='ui/help.html'), name='help'),
    url(r'^help/pages$', TemplateView.as_view(template_name='ui/help_pages.html'), name='help_pages'),
    url(r'^help/formats$', TemplateView.as_view(template_name='ui/help_formats.html'), name='help_formats'),
    url(r'^help/tags$', TemplateView.as_view(template_name='ui/help_tags.html'), name='help_tags'),
    url(r'^help/config$', TemplateView.as_view(template_name='ui/help_config.html'), name='help_config'),
)

urlpatterns += i18n_patterns('registration.views',
    url(r'^accounts/', include('registration.backends.default.urls')),
)

urlpatterns += i18n_patterns('admin.views',
    url(r'^admin/', include(admin.site.urls)),
)

# don't apply i18n patterns here.. api uses Accept-Language header
urlpatterns += patterns('api.views',
    url(r'^api/', include(router.urls, namespace='api')),
    url(r'^api/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/rerun$', RunJob.as_view(), name='rerun'),
    url(r'^api/hdm-data-model$', HDMDataModelView.as_view(), name='hdm-data-model'),
    url(r'^api/osm-data-model$', OSMDataModelView.as_view(), name='osm-data-model'),
)


