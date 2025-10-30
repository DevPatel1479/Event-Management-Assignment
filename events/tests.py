from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from events.models import Event, RSVP, Review


class EventAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username="dev", password="test123")
        self.user2 = User.objects.create_user(username="tmp", password="test123")

        self.public_event = Event.objects.create(
            organizer=self.user1,
            title="Public Event",
            description="Test public event",
            location="Online",
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=2),
            is_public=True
        )

        self.private_event = Event.objects.create(
            organizer=self.user1,
            title="Private Event",
            description="Test private event",
            location="Offline",
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=2),
            is_public=False
        )
        self.private_event.invited_users.add(self.user2)

    def authenticate(self, user):
        """Helper: forces authentication for APIClient."""
        self.client.force_authenticate(user=user)

    def test_list_events_public(self):
        """✅ Only public events visible to unauthenticated users."""
        response = self.client.get("/api/events/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Public Event")

    def test_private_event_visible_to_invited(self):
        """✅ Invited users can see private events."""
        self.authenticate(self.user2)
        response = self.client.get("/api/events/")
        titles = [e["title"] for e in response.data["results"]]
        self.assertIn("Private Event", titles)

    def test_create_event_authenticated(self):
        """✅ Authenticated user can create an event."""
        self.authenticate(self.user2)
        payload = {
            "title": "New Event",
            "description": "Created via test",
            "location": "Remote",
            "start_time": (timezone.now() + timedelta(days=1)).isoformat(),
            "end_time": (timezone.now() + timedelta(days=1, hours=2)).isoformat(),
            "is_public": True
        }
        response = self.client.post("/api/events/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["organizer"], "tmp")

    def test_edit_event_by_invited_user_forbidden(self):
        """❌ Invited users cannot edit organizer's event."""
        self.authenticate(self.user2)
        url = f"/api/events/{self.private_event.id}/"
        response = self.client.put(url, {"title": "Edited by invited"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class RSVPTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="tmp", password="test123")
        self.event = Event.objects.create(
            organizer=self.user,
            title="RSVP Event",
            description="RSVP testing",
            location="Test",
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=2),
            is_public=True
        )
        self.client.force_authenticate(user=self.user)

    def test_create_rsvp(self):
        """✅ User can RSVP to an event."""
        url = f"/api/events/{self.event.id}/rsvp/"
        payload = {"status": "Going"}
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_duplicate_rsvp_updates_status(self):
        """✅ Second RSVP updates existing record instead of duplicating."""
        RSVP.objects.create(user=self.user, event=self.event, status="Going")
        url = f"/api/events/{self.event.id}/rsvp/"
        payload = {"status": "Not Going"}
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(RSVP.objects.count(), 1)
        self.assertEqual(RSVP.objects.first().status, "Not Going")


class ReviewAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="tmp", password="test123")
        self.event = Event.objects.create(
            organizer=self.user,
            title="Review Event",
            description="Review testing",
            location="Test",
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=2),
            is_public=True
        )
        self.client.force_authenticate(user=self.user)

    def test_create_review(self):
        """✅ User can create review for an event."""
        url = f"/api/events/{self.event.id}/reviews/"
        payload = {"rating": 5, "comment": "Great event!"}
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 1)

    def test_list_reviews(self):
        """✅ List reviews for event."""
        Review.objects.create(user=self.user, event=self.event, rating=4, comment="Good")
        url = f"/api/events/{self.event.id}/reviews/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
