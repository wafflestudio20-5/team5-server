from rest_framework import permissions

from styles.models import Profile, Post


class IsProfileOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj: Profile):
        return bool(
            request.method in permissions.SAFE_METHODS or
            request.user and request.user.is_authenticated and
            request.user == obj.user
        )


class IsPostWriterOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj: Post):
        return bool(
            request.method in permissions.SAFE_METHODS or
            request.user and request.user.is_authenticated and
            request.user == obj.created_by.user
        )
