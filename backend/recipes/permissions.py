from rest_framework import permissions


class RecipesPermission(permissions.BasePermission):
    """Пермишены для `RecipeView`."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            or request.method in permissions.SAFE_METHODS
        )

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            return (
                obj.author == request.user
                or request.user.is_admin
                or request.user.is_superadmin
            )
