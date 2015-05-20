"""
hot_exports URL Configuration
"""
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from ui import urls as ui_urls
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from api.urls import router


urlpatterns = []

urlpatterns += i18n_patterns('ui.views',
    url(r'^$', include(ui_urls)),
)

urlpatterns += i18n_patterns(
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(router.urls, namespace='api')),
    url(r'^api/', include('rest_framework.urls', namespace='rest_framework')),
)

