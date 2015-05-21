"""
HOT Exports URL Configuration
"""
from django.conf.urls import include, url, patterns
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from ui import urls as ui_urls
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from api.urls import router

urlpatterns = []

urlpatterns += patterns('ui.views',
    url(r'^$', TemplateView.as_view(template_name='ui/index.html'), name='index'),
    url(r'^jobs/', include(ui_urls)),
)

urlpatterns += patterns('api.views',
    url(r'^api/', include(router.urls, namespace='api')),
    url(r'^api/', include('rest_framework.urls', namespace='rest_framework')),
)

urlpatterns += patterns('admin.views',
    url(r'^admin/', include(admin.site.urls)),
)

