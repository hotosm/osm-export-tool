import django_filters
from jobs.models import Job


class JobFilter(django_filters.FilterSet):
    
    name = django_filters.CharFilter(name="name",lookup_type="icontains")
    description = django_filters.CharFilter(name="description",lookup_type="icontains")
    event = django_filters.CharFilter(name="event", lookup_type="icontains")
    created = django_filters.DateTimeFilter(name="created_at",lookup_type="exact")
    region = django_filters.CharFilter(name="region__name")
    
    class Meta:
        model = Job
        fields = ('name', 'description', 'event', 'created', 'region',)