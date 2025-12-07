from rest_framework import permissions

class IsPartner(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'partner') and
            request.user.partner is not None
        )

class IsOwnerOfCoupon(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.partner == request.user.partner