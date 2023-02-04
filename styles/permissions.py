from rest_framework import permissions

from styles.models import Profile, Post, Comment, Reply


class IsProfileOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj: Profile):
        return bool(
            request.method in permissions.SAFE_METHODS or
            request.user and request.user.is_authenticated and
            request.user == obj.user
        )


class IsWriterOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj: Post | Comment | Reply):
        return bool(
            request.method in permissions.SAFE_METHODS or
            request.user and request.user.is_authenticated and
            request.user == obj.created_by.user
        )