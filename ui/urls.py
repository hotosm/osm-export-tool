from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

urlpatterns = patterns('ui.views',
    url(r'^$', TemplateView.as_view(template_name='ui/list.html'), name='list'),
    url(r'^create/$', TemplateView.as_view(template_name='ui/create.html'), name='create'),
    url(r'^edit/$', TemplateView.as_view(template_name='ui/edit.html'), name='edit'),
    url(r'^help/$', TemplateView.as_view(template_name='ui/edit.html'), name='edit'),
)