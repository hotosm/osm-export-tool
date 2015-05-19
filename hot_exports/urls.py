"""
hot_exports URL Configuration
"""
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from ui import urls as ui_urls
from django.views.generic import TemplateView

urlpatterns = []

urlpatterns += i18n_patterns(
    url(r'^admin/', include(admin.site.urls)),
    url('', include(ui_urls)),
)

