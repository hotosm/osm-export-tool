import logging
import pdb
from rest_framework import serializers
from datetime import datetime
from jobs.models import Job, ExportFormat
from django.contrib.auth.models import User, Group
from django.utils import timezone


try:
    from collections import OrderedDict
# python 2.6
except ImportError:
    from ordereddict import OrderedDict

# Get an instance of a logger
logger = logging.getLogger(__name__)

"""
class GroupSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()


class UserGroupSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    groups = GroupSerializer(many=True)
"""


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class ExportFormatSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
       view_name='api:formats-detail',
    )

    class Meta:
        model = ExportFormat
        fields = ('id', 'url', 'name', 'description', 'cmd')


class JobSerializer(serializers.ModelSerializer):
    """ Job Serializer"""

    """
    formats = serializers.HyperlinkedRelatedField(
        view_name='api:formats-detail',
        many=True,
        queryset = ExportFormat.objects.all()
    )
    """
    
    #formats = ExportFormatSerializer()

    url = serializers.HyperlinkedIdentityField(
        view_name='api:jobs-detail',
    )

    class Meta:
        model = Job
        fields = ('id', 'name', 'url', 'description',
                  'created_at', 'formats', 'status')

    def to_internal_value(self, data):
        request = self.context['request']
        user = request.user
        job_name = data['name']
        description = data['description']
        updated_at = timezone.now()
        return {'name': job_name, 'description': description, 'user': user, 'updated_at': updated_at}
