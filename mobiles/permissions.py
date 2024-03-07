from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, _, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return obj.seller == request.user
