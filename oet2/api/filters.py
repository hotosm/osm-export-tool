"""Module providing classes to filter api results."""
# -*- coding: utf-8 -*-
import logging

import django_filters

from django.db.models import Q

from oet2.jobs.models import ExportConfig, Job
from oet2.tasks.models import ExportRun

logger = logging.getLogger(__name__)


class JobFilter(django_filters.FilterSet):
    """Filter export results according to a range of critera."""
    name = django_filters.CharFilter(name="name", lookup_type="icontains")
    description = django_filters.CharFilter(name="description", lookup_type="icontains")
    event = django_filters.CharFilter(name="event", lookup_type="icontains")
    start = django_filters.DateTimeFilter(name="created_at", lookup_type="gte")
    end = django_filters.DateTimeFilter(name="created_at", lookup_type="lte")
    region = django_filters.CharFilter(name="region__name")
    user = django_filters.CharFilter(name="user__username", lookup_type="exact")
    feature = django_filters.CharFilter(name="tags__name", lookup_type="icontains")
    published = django_filters.BooleanFilter(name="published", lookup_type="exact")
    user_private = django_filters.MethodFilter(action='user_private_filter')

    class Meta:
        model = Job
        fields = ('name', 'description', 'event', 'start', 'end', 'region',
                  'user', 'user_private', 'feature', 'published')
        order_by = ('-created_at',)

    def user_private_filter(self, queryset, value):
        """
        Filter export results by user and/or published status.

        Return exports for the specified user where exports are either published or unpublished.
        OR
        Return exports for all other users and where the export is published.
        """
        return queryset.filter(
            (Q(user__username=value) | (~Q(user__username=value) & Q(published=True)))
        )


class ExportRunFilter(django_filters.FilterSet):
    """Filter export runs by status."""
    status = django_filters.CharFilter(name="status", lookup_type="icontains")

    class Meta:
        model = ExportRun
        fields = ('status',)
        order_by = ('-started_at',)


class ExportConfigFilter(django_filters.FilterSet):
    """Filter export configurations."""
    name = django_filters.CharFilter(name="name", lookup_type="icontains")
    config_type = django_filters.CharFilter(name="config_type", lookup_type="icontains")
    start = django_filters.DateTimeFilter(name="created_at", lookup_type="gte")
    end = django_filters.DateTimeFilter(name="created_at", lookup_type="lte")
    user = django_filters.CharFilter(name="user__username", lookup_type="exact")
    published = django_filters.BooleanFilter(name="published", lookup_type="exact")
    user_private = django_filters.MethodFilter(action='user_private_filter')

    class Meta:
        model = ExportConfig
        fields = ('name', 'config_type', 'start', 'end', 'user', 'published', 'user_private')
        order_by = ('-created_at',)

    def user_private_filter(self, queryset, value):
        """
        Filter export configurations by user and/or published status.

        Return configurations for the specified user where configurations are either published or unpublished.
        OR
        Return configurations for all other users and where the configuration is published.
        """
        return queryset.filter(
            (Q(user__username=value) | (~Q(user__username=value) & Q(published=True)))
        )
