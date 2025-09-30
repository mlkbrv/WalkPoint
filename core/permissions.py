from rest_framework.permissions import BasePermission

class IsPartner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, "partner_account")
