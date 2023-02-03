from rest_framework.pagination import PageNumberPagination, CursorPagination


class CustomPagination(PageNumberPagination):
    page_size = 40


class CommonCursorPagination(CursorPagination):
    # page_size = 20
    page_size = 5
    ordering = 'created_at'

class RecentCursorPagination(CursorPagination):
    # page_size = 20
    page_size = 5
    ordering = 'created_at'
