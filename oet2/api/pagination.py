"""Provides pagination for api results."""
# -*- coding: utf-8 -*-
import logging

from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

logger = logging.getLogger(__name__)


class LinkHeaderPagination(PageNumberPagination):
    """
    Paginate API results using the HTTP 'Link' and 'Content-Range' headers.

    More information at http://www.django-rest-framework.org/api-guide/pagination/#header-based-pagination
    """
    page_size = 10  # default page size
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        """Return the paginated response."""
        next_url = self.get_next_link()
        previous_url = self.get_previous_link()
        status_code = status.HTTP_206_PARTIAL_CONTENT
        if next_url is not None and previous_url is not None:
            link = '<{next_url}>; rel="next", <{previous_url}>; rel="prev"'
        elif next_url is not None:
            link = '<{next_url}>; rel="next"'
        elif previous_url is not None:
            link = '<{previous_url}>; rel="prev"'
        else:
            link = ''
            status_code = status.HTTP_200_OK
        link = link.format(next_url=next_url, previous_url=previous_url)
        start_idx = self.page.start_index()
        end_idx = self.page.end_index()
        total = self.page.paginator.count
        content_range_header = 'results {0}-{1}/{2}'.format(start_idx, end_idx, total)
        headers = {'Link': link, 'Content-Range': content_range_header} if link else {'Content-Range': content_range_header}
        return Response(data, headers=headers, status=status_code)
