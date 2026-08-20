from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """Allows access only to users with role=ADMIN."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin_role)


class IsFacultyRole(BasePermission):
    """Allows access only to users with role=FACULTY."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_faculty_role)


class IsAdminOrFaculty(BasePermission):
    """Allows any authenticated Admin or Faculty user (i.e. anyone logged in)."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
