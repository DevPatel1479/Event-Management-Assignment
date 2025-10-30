from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, RSVPViewSet, RSVPUpdateView,  ReviewViewSet

router = DefaultRouter()
router.register(r'events', EventViewSet, basename='event')

urlpatterns = [
    path('', include(router.urls)),
    path('events/<int:event_id>/rsvp/', RSVPViewSet.as_view({'post': 'create'})),
    path('events/<int:event_id>/rsvp/<int:user_id>/', RSVPUpdateView.as_view(), name='rsvp-update'),
    path('events/<int:event_id>/reviews/', ReviewViewSet.as_view({'get': 'list', 'post': 'create'})),

]
