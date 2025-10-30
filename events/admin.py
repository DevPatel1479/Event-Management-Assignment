from django.contrib import admin
from .models import UserProfile, Event, RSVP, Review

# ==============================
# Admin registrations
# ==============================

# Display UserProfile with user and full name in admin panel
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'location')
    search_fields = ('full_name', 'location', 'user__username')


# Display Event model with useful fields for easy management
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'organizer', 'location', 'start_time', 'end_time', 'is_public')
    list_filter = ('is_public', 'start_time')
    search_fields = ('title', 'description', 'organizer__username', 'location')
    filter_horizontal = ('invited_users',)


# Display RSVP model showing event, user, and status
@admin.register(RSVP)
class RSVPAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'status')
    list_filter = ('status',)
    search_fields = ('event__title', 'user__username')


# Display Review model showing event, user, and rating
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('event__title', 'user__username', 'comment')
