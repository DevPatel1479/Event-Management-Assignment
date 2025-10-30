# permissions.py
from rest_framework import permissions

class IsOrganizerOrInvitedOrReadOnly(permissions.BasePermission):
    """
    Allow safe (GET) access to public events for everyone.
    Allow private events only for organizer or invited users.
    Organizer can edit/delete.
    """

    def has_object_permission(self, request, view, obj):
        # Anyone can read public events
        if obj.is_public and request.method in permissions.SAFE_METHODS:
            return True

        # Organizer can always modify their event
        if obj.organizer == request.user:
            return True

        # Invited users can view private events
        if not obj.is_public and request.method in permissions.SAFE_METHODS:
            if request.user.is_authenticated and request.user in obj.invited_users.all():
                return True

        return False
