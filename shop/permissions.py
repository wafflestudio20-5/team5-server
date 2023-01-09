from rest_framework import permissions

<<<<<<< HEAD
from shop.models import Wish, Product

=======
>>>>>>> dbd7018c9e9ad3c9ffe2213f0eb9d4455bb94aaa

class IsAdminUserOrReadOnly(permissions.BasePermission):
    message = {'Error': 'If you are not a superuser, only reading is allowed'}

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return request.user.is_superuser


class IsAuthenticatedOrReadInfo(permissions.BasePermission):
    message = {'Error': 'If you are not authenticated, you cannot see other sizes'}

<<<<<<< HEAD
    def has_permission(self, request, view):
        if view.kwargs['size'] == 'ALL':
            if request.user.is_authenticated or (request.method in permissions.SAFE_METHODS):
                return True
            else:
                return False
        else:
            if request.user.is_authenticated:
                return True
            else:
                return False
=======
    def has_object_permission(self, request, view, obj):
        if obj.size != 'ALL' and not request.user.is_authenticated:
            return False
        return True
>>>>>>> dbd7018c9e9ad3c9ffe2213f0eb9d4455bb94aaa

