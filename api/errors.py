from django.http import HttpResponse
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.renderers import JSONRenderer

# API Error Responses

class MissingFormatErrorAPIResponse(HttpResponse):
    """
    Structured error response for missing export format(s).
    
    """
    def __init__(self, request=None, *args, **kwargs):
        scheme = request.scheme
        host = request.META['HTTP_HOST']
        data = {'id': 'missing_format',
                'message': 'Job cannot be created without specifying a export format uid.',
                'formats_url': '{0}://{1}{2}'.format(scheme, host, reverse('api:formats-list'))
        }
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json; version=1.0'
        super(MissingFormatErrorAPIResponse, self).__init__(content, **kwargs)
