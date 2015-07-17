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
from api.views import HDMDataModelView, OSMDataModelView

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
    url(r'^api/data-model-hdm$', HDMDataModelView.as_view(), name='data-model-hdm'),
    url(r'^api/data-model-osm$', OSMDataModelView.as_view(), name='data-model-osm'),
)

urlpatterns += patterns('admin.views',
    url(r'^admin/', include(admin.site.urls)),
)

