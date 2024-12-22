from rest_framework.permissions import BasePermission

from .models import UserRole


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated or not request.user:
            return False
        return request.user.role == UserRole.ADMIN.value


class IsUser(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated or not request.user:
            return False
        return request.user.role == UserRole.USER.value


class IsGuest(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated or not request.user:
            return False
        return request.user.role == UserRole.GUEST.value


class IsSuperuser(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated or not request.user:
            return False
        return request.user.is_superuser
