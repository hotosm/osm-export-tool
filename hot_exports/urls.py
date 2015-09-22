"""
HOT Exports URL Configuration
"""
from django.conf.urls import include, url, patterns
from django.conf.urls.i18n import i18n_patterns
from django.contrib.auth.decorators import login_required
from django.contrib import admin
from django.contrib import auth
from ui import urls as ui_urls
from ui.views import create_error_view
from django.views.generic import TemplateView
from django.views.i18n import javascript_catalog
from rest_framework.routers import DefaultRouter
from api.urls import router
from api.views import HDMDataModelView, OSMDataModelView, RunJob

admin.autodiscover()

urlpatterns = []

urlpatterns += i18n_patterns('ui.views',
    url(r'^$', login_required(TemplateView.as_view(template_name='ui/index.html')), name='index'),
    url(r'^exports/', include(ui_urls)),
    url(r'^login/$', TemplateView.as_view(template_name='osm/login.html'), name="login"), 
    url(r'^logout$', 'logout', name='logout'),
    url(r'^error$', create_error_view, name='error'),
    url(r'^update$', TemplateView.as_view(template_name='ui/upgrade.html'), name='update'),
    url(r'^email/$', 'require_email', name='require_email'),
)

urlpatterns += i18n_patterns('ui.help',
    url(r'^about$', TemplateView.as_view(template_name='ui/about.html'), name='about'),
    url(r'^help$', TemplateView.as_view(template_name='ui/help.html'), name='help'),
    url(r'^help/pages$', TemplateView.as_view(template_name='ui/help_pages.html'), name='help_pages'),
    url(r'^help/formats$', TemplateView.as_view(template_name='ui/help_formats.html'), name='help_formats'),
    url(r'^help/tags$', TemplateView.as_view(template_name='ui/help_tags.html'), name='help_tags'),
    url(r'^help/config$', TemplateView.as_view(template_name='ui/help_config.html'), name='help_config'),
)

urlpatterns += i18n_patterns('admin.views',
    url(r'^admin/', include(admin.site.urls)),
)

# OAuth urls
urlpatterns += i18n_patterns('ui.social',
    url('^osm/', include('social.apps.django_app.urls', namespace='osm')),
    url('^osm/email_verify_sent/$', TemplateView.as_view(template_name='osm/email_verify_sent.html'), name='email_verify_sent'),
    url('^osm/error$', TemplateView.as_view(template_name='osm/error.html'), name='login_error')
)

# don't apply i18n patterns here.. api uses Accept-Language header
urlpatterns += patterns('api.views',
    url(r'^api/', include(router.urls, namespace='api')),
    url(r'^api/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/rerun$', RunJob.as_view(), name='rerun'),
    url(r'^api/hdm-data-model$', HDMDataModelView.as_view(), name='hdm-data-model'),
    url(r'^api/osm-data-model$', OSMDataModelView.as_view(), name='osm-data-model'),
)

# i18n for js
js_info_dict = {
    'packages': ('hot_osm',),
}

urlpatterns += patterns('',
    url(r'^jsi18n/$', javascript_catalog, js_info_dict),
    url(r'^i18n/', include('django.conf.urls.i18n')),
)

handler500 = 'ui.views.internal_error_view'

handler404 = 'ui.views.not_found_error_view'


