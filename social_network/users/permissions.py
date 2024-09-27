from rest_framework.permissions import BasePermission

class IsReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in ['GET']

class IsWriter(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Write').exists()

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff or request.user.groups.filter(name='Admin').exists()
