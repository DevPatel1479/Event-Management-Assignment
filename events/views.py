from rest_framework import viewsets, generics, permissions
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from .models import Event, RSVP, Review
from .serializers import EventSerializer, RSVPSerializer, ReviewSerializer
from .permissions import IsOrganizerOrInvitedOrReadOnly
from .tasks import send_event_email


# ================================================
# Custom Pagination for Events
# ================================================
# Controls how many event records appear per page in API responses
class EventPagination(PageNumberPagination):
    page_size = 5  # Default number of events per page
    page_size_query_param = 'page_size'  # Allows client to customize page size using a query parameter
    max_page_size = 50  # Maximum limit for page size to prevent heavy responses


# ================================================
# Event ViewSet
# ================================================
# Handles CRUD operations for Event model
# Includes filtering logic to show only accessible events for each user
class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [IsOrganizerOrInvitedOrReadOnly]  # Custom permission: organizers or invited users can modify
    pagination_class = EventPagination  # Use custom pagination defined above

    def get_queryset(self):
        """
        Returns filtered event list depending on the user's authentication status:
        - Authenticated users: Can see public, their own, or invited events.
        - Anonymous users: Only see public events.
        """
        user = self.request.user

        # If user is viewing all events
        if self.action == 'list':
            if user.is_authenticated:
                # Authenticated users can see their own, invited, or public events
                return Event.objects.filter(
                    Q(is_public=True) | 
                    Q(organizer=user) | 
                    Q(invited_users=user)
                ).distinct().order_by('-created_at')
            else:
                # Non-logged-in users can only see public events
                return Event.objects.filter(is_public=True).order_by('-created_at')

        # For specific event detail view, return all (permission class will control access)
        return Event.objects.all().order_by('-created_at')

    def perform_create(self, serializer):
        """
        Automatically sets the logged-in user as the event organizer upon creation.
        Also triggers an asynchronous email notification using Celery.
        """
        event = serializer.save(organizer=self.request.user)
        send_event_email.delay(event.id)  # Send email in background


