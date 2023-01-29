from rest_framework.pagination import PageNumberPagination, CursorPagination


class CustomPagination(PageNumberPagination):
    page_size = 40


class CustomCursorPagination(CursorPagination):
    page_size = 40
    page_query_param = 'page'
    ordering = '-created_at'
