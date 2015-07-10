import logging
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)

class JobLinkHeaderPagination(PageNumberPagination):
    
    page_size = 5
    
    def get_paginated_response(self, data):
        next_url = self.get_next_link()
        previous_url = self.get_previous_link()
        status_code = status.HTTP_206_PARTIAL_CONTENT
        if next_url is not None and previous_url is not None:
            link = '<{next_url}; rel="next">, <{previous_url}; rel="prev">'
        elif next_url is not None:
            link = '<{next_url}; rel="next">'
        elif previous_url is not None:
            link = '<{previous_url}; rel="prev">'
        else:
            link = ''
            status_code = status.HTTP_200_OK
        link = link.format(next_url=next_url, previous_url=previous_url)
        
        logger.debug('Total results: %s' % self.page.paginator.count)
        logger.debug('Num pages: %s' % self.page.paginator.num_pages)
        logger.debug('Page range: %s' % self.page.paginator.page_range)
        logger.debug('Page number: %s' % self.page.number)
        start_idx = self.page.start_index()
        end_idx = self.page.end_index()
        total = self.page.paginator.count
        content_range_header = 'jobs {0}-{1}/{2}'.format(start_idx, end_idx, total)
        headers = {'Link': link, 'Content-Range': content_range_header} if link else {'Content-Range': content_range_header}
        return Response(data, headers=headers, status=status_code)