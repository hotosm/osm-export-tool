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

urlpatterns += patterns('ui.views',
    url(r'^$', login_required(TemplateView.as_view(template_name='ui/index.html')), name='index'),
    url(r'^help$', TemplateView.as_view(template_name='ui/help.html'), name='help'),
    url(r'^jobs/', include(ui_urls)),
)

urlpatterns += patterns('registration.views',
    url(r'^accounts/', include('registration.backends.default.urls')),
)

urlpatterns += patterns('api.views',
    url(r'^api/', include(router.urls, namespace='api')),
    url(r'^api/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/rerun$', RunJob.as_view(), name='rerun'),
    url(r'^api/hdm-data-model$', HDMDataModelView.as_view(), name='hdm-data-model'),
    url(r'^api/osm-data-model$', OSMDataModelView.as_view(), name='osm-data-model'),
)

urlpatterns += patterns('admin.views',
    url(r'^admin/', include(admin.site.urls)),
)

