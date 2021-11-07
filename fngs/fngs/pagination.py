from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.status import *


class Pagination(PageNumberPagination):
    page_size = 50
    max_page_size = 100
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        if self.page_size_query_param in self.request.query_params \
                and int(self.request.query_params[self.page_size_query_param]) > self.max_page_size:
            return Response({'error': f'Requested page size {self.request.query_params[self.page_size_query_param]} is more than max allowed page size {self.max_page_size}'},
                            HTTP_400_BAD_REQUEST)
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
            },
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'page_size': self.request.query_params[self.page_size_query_param] \
                         if self.page_size_query_param in self.request.query_params \
                         else self.page_size,
            'results': data,
        })
