from django.db import models
from django.contrib.auth.models import User

# ==============================
#  UserProfile Model
# ==============================
# Extends Django's built-in User model to store additional user information
class UserProfile(models.Model):
    # One-to-one relation with User (each user has one profile)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)  # User’s full name
    bio = models.TextField(blank=True)  # Short description about the user
    location = models.CharField(max_length=100, blank=True)  # User’s location
    profile_picture = models.ImageField(upload_to='profiles/', blank=True)  # Profile picture upload path

    def __str__(self):
        return self.full_name


# ==============================
#  Event Model
# ==============================
# Represents an event organized by a user
class Event(models.Model):
    title = models.CharField(max_length=200)  # Event title
    description = models.TextField()  # Event details/description
    organizer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='organized_events'
    )  # Event creator (User)
    location = models.CharField(max_length=100)  # Event location
    start_time = models.DateTimeField()  # Event start datetime
    end_time = models.DateTimeField()  # Event end datetime
    is_public = models.BooleanField(default=True)  # Visibility flag for event
    invited_users = models.ManyToManyField(
        User, related_name="invited_events", blank=True
    )  # Users invited to this event
    created_at = models.DateTimeField(auto_now_add=True)  # Auto timestamp on creation
    updated_at = models.DateTimeField(auto_now=True)  # Auto timestamp on update

    def __str__(self):
        return self.title


# ==============================
#  RSVP Model
# ==============================
# Tracks user attendance response for a specific event
class RSVP(models.Model):
    STATUS_CHOICES = [
        ('Going', 'Going'),
        ('Maybe', 'Maybe'),
        ('Not Going', 'Not Going'),
    ]
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name='rsvps'
    )  # Related event
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User responding to event
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='Maybe'
    )  # RSVP status

    class Meta:
        unique_together = ('event', 'user')  # Prevent duplicate RSVPs for same user & event

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"


# ==============================
#  Review Model
# ==============================
# Stores user feedback for an event
class Review(models.Model):
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name='reviews'
    )  # Event being reviewed
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Reviewer (User)
    rating = models.PositiveIntegerField(default=1)  # Rating value (e.g., 1–5)
    comment = models.TextField(blank=True)  # Optional review comment
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp on creation

    def __str__(self):
        return f"Review by {self.user.username} for {self.event.title}"
