from rest_framework.permissions import BasePermission


class AdminOrManagerPerm(BasePermission):
    """Разрешения на обновление."""

    def has_permission(self, request, view):
        if request.user.is_staff or request.user.is_superuser:
            return True
