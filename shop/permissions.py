from rest_framework import permissions

from shop.models import SalesBid, PurchaseBid, Comment, Reply


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


class IsWriterOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj: Comment | Reply):
        return bool(
            request.method in permissions.SAFE_METHODS or
            request.user and request.user.is_authenticated and
            request.user == obj.created_by.user
        )

