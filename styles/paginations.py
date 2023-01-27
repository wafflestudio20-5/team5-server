from rest_framework.pagination import CursorPagination


class CustomCursorPagination(CursorPagination):
    # page_size = 20
    page_size = 5
    ordering = '-created_at'
