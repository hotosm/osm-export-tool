from django.http import HttpResponse
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.renderers import JSONRenderer

# API Error Responses

class MissingFormatAPIResponse(HttpResponse):
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
        super(MissingFormatAPIResponse, self).__init__(content, **kwargs)


class MissingParamAPIResponse(HttpResponse):
    """
    Structured error response for missing bounding box parameter(s).
    
    """
    def __init__(self, request=None, *args, **kwargs):
        scheme = request.scheme
        host = request.META['HTTP_HOST']
        expected_params = ['xmin','ymin','xmax','ymax','name','description', 'user', 'formats']
        missing_params = [expected for expected in expected_params if expected not in request.data.keys()]
        missing_str = '[' + ', '.join(missing_params) + ']'
        data = {'id': 'missing_parameter',
                'message': 'Missing parameter(s): {0}'.format(missing_str)
        }
        
        
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json; version=1.0'
        super(MissingParamAPIResponse, self).__init__(content, **kwargs)


class Error(Exception):
    """Exception base class."""
    pass


class InvalidBBOXError(Error):
    """
    Exception raised for invalid bounding box.

    Attributes:
        msg  -- explanation of the error
    """

    def __init__(self, msg):
        self.status = status.HTTP_400_BAD_REQUEST
        self.msg = msg