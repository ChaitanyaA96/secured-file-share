from rest_framework.permissions import BasePermission
from .models import UserRole

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == UserRole.ADMIN.value
    
class IsUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == UserRole.USER.value

class IsGuest(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == UserRole.GUEST.value    