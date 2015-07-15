import logging
import pdb
import django_filters
from jobs.models import Job

logger = logging.getLogger(__name__)

class JobFilter(django_filters.FilterSet):
    
    name = django_filters.CharFilter(name="name",lookup_type="icontains")
    description = django_filters.CharFilter(name="description",lookup_type="icontains")
    event = django_filters.CharFilter(name="event", lookup_type="icontains")
    start = django_filters.DateTimeFilter(name="created_at", lookup_type="gte")
    end = django_filters.DateTimeFilter(name="created_at", lookup_type="lte")
    region = django_filters.CharFilter(name="region__name")
    user = django_filters.CharFilter(name="user__username", lookup_type="exact")
    
    class Meta:
        model = Job
        fields = ('name', 'description', 'event', 'start', 'end', 'region', 'user',)
        order_by = ('-created_at',)
        