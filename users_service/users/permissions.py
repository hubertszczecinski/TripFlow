from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def is_admin(self, request) -> bool:
        if request.user.is_authenticated and request.user.role == "ADMIN":
            return True
        return False
        
class IsHR(BasePermission):
    def is_hr(self, request) -> bool:
        if request.user.is_authenticated and request.user.role == "HR":
            return True
        return False
        
class IsFinance(BasePermission):
    def is_finance(self, request) -> bool:
        if request.user.is_authenticated and request.user.role == "FINANCE":
            return True
        return False
        
class IsUser(BasePermission):
    def is_user(self, request) -> bool:
        if request.user.is_authenticated and request.user.role == "USER":
            return True
        return False