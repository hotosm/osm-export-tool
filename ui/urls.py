from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

urlpatterns = patterns('ui.views',
    url(r'^$', TemplateView.as_view(template_name='ui/list.html'), name='list'),
    url(r'^create/$', login_required(TemplateView.as_view(template_name='ui/create.html')), name='create'),
    url(r'^(?P<uuid>[^/]+)/$', TemplateView.as_view(template_name='ui/detail.html'), name='detail'),
    url(r'^clone/(?P<uuid>[^/]+)/$', TemplateView.as_view(template_name='ui/clone.html'), name='clone')
)