from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self,request,view):

        if not request.user or not request.user.is_authenticated:
            return False
        
        return request.user.role == 'admin'

class IsUser(BasePermission):
    def has_permission(self,request,view):
        return request.user.role == 'user'