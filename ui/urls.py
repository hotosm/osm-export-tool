from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from .views import create_export, clone_export

urlpatterns = patterns('ui.views',
    url(r'^$', TemplateView.as_view(template_name='ui/list.html'), name='list'),
    url(r'^create/$', login_required(create_export), name='create'),
    url(r'^configurations/$', TemplateView.as_view(template_name='ui/configurations.html'), name='configurations'),
    url(r'^(?P<uuid>[^/]+)/$', TemplateView.as_view(template_name='ui/detail.html'), name='detail'),
    url(r'^clone/(?P<uuid>[^/]+)/$', login_required(clone_export), name='clone')
)