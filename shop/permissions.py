from rest_framework import permissions

from shop.models import SalesBid, PurchaseBid


class IsAdminUserOrReadOnly(permissions.BasePermission):
    message = {'Error': 'If you are not a superuser, only reading is allowed'}

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return request.user.is_superuser


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj:PurchaseBid | SalesBid):
        if request.user.is_authenticated and obj.user == request.user:
            return True
        return False


# class IsAuthenticatedOrReadInfo(permissions.BasePermission):
#     message = {'Error': 'If you are not authenticated, you cannot see other sizes'}
#
#     def has_permission(self, request, view):
#         if view.kwargs['size'] == 'ALL':
#             if request.user.is_authenticated or (request.method in permissions.SAFE_METHODS):
#                 return True
#             else:
#                 return False
#         else:
#             if request.user.is_authenticated:
#                 return True
#             else:
#                 return False
#
#     c

