from rest_framework import permissions

from users.models import User


class IsAdminPermission(permissions.BasePermission):
    """Разрешения уровня `администратор`."""
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return (
                request.user.role == User.ADMIN
                or request.user.is_superuser
            )
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            return (
                request.user.role == User.ADMIN
                or request.user.is_superuser
            )
        return False


class IsUserPermission(permissions.BasePermission):
    """Разрешения уровня `авторизированный пользователь`."""
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class RecipesPermission(permissions.BasePermission):
    """Пермишены для `RecipeView`."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            or request.method in permissions.SAFE_METHODS
        )

    def has_object_permission(self, request, view, obj):
        return (
            obj.author == request.user
            or request.user.role == User.ADMIN
            or request.user.is_superadmin
        )
