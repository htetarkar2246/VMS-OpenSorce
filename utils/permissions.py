from rest_framework.permissions import BasePermission


class IsManagerOrReadOnly(BasePermission):
    """Allow read access to authenticated users and writes to managers only."""

    def has_permission(self, request, view):
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return request.user and request.user.is_authenticated

        return (
            request.user
            and request.user.is_authenticated
            and (
                request.user.role == "MANAGER"
                or request.user.is_superuser
            )
        )


class IsManagerOrSupervisorOrReadOnly(BasePermission):
    """Allow write access to managers and supervisors."""

    def has_permission(self, request, view):
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return request.user and request.user.is_authenticated

        return (
            request.user
            and request.user.is_authenticated
            and (
                request.user.role in ["MANAGER", "SUPERVISOR"]
                or request.user.is_superuser
            )
        )


class IsManagerSupervisorLeaderOrReadOnly(BasePermission):
    """Allow write access to managers, supervisors, and team leaders."""

    def has_permission(self, request, view):
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return request.user and request.user.is_authenticated

        return (
            request.user
            and request.user.is_authenticated
            and (
                request.user.role in ["MANAGER", "SUPERVISOR", "LEADER"]
                or request.user.is_superuser
            )
        )
