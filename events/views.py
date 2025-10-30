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


# ================================================
# RSVP ViewSet
# ================================================
# Manages RSVP (attendance) responses for events
class RSVPViewSet(viewsets.ModelViewSet):
    serializer_class = RSVPSerializer
    queryset = RSVP.objects.all()
    permission_classes = [permissions.IsAuthenticated]  # Only logged-in users can RSVP

    def perform_create(self, serializer):
        """
        Prevents duplicate RSVPs for the same user and event.
        If RSVP exists → update status.
        Else → create a new RSVP entry.
        """
        event_id = self.kwargs.get("event_id")
        event = get_object_or_404(Event, id=event_id)

        # Check if RSVP already exists
        existing_rsvp = RSVP.objects.filter(event=event, user=self.request.user).first()
        if existing_rsvp:
            # Update existing RSVP instead of creating a duplicate
            existing_rsvp.status = serializer.validated_data.get("status", existing_rsvp.status)
            existing_rsvp.save()
        else:
            # Create a new RSVP record
            serializer.save(user=self.request.user, event=event)

    def get_queryset(self):
        """
        Returns all RSVPs related to a specific event.
        """
        event_id = self.kwargs.get("event_id")
        return RSVP.objects.filter(event_id=event_id)


# ================================================
# RSVP Update View
# ================================================
# Handles updating RSVP status using generic UpdateAPIView
class RSVPUpdateView(generics.UpdateAPIView):
    serializer_class = RSVPSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        Retrieves a specific RSVP record based on event_id and user_id from URL.
        """
        event_id = self.kwargs['event_id']
        user_id = self.kwargs['user_id']
        print(user_id)  # Debugging/logging purpose
        return get_object_or_404(RSVP, event_id=event_id, user_id=user_id)
