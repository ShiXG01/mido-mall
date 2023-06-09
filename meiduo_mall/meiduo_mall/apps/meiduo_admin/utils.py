from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


# 重写JWT返回结果方法
def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'username': user.username,
        'id': user.id,
    }


# 自定义分页器
class PageNum(PageNumberPagination):
    page_size_query_param = 'pagesize'
    max_page_size = 10

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'list': data,
            'page': self.page.number,
            'pages': self.page.paginator.num_pages,
            'pagesize': self.max_page_size
        })
