from celery import shared_task
from django.core.mail import send_mail
from .models import Event

# Define a shared Celery task to send event notification emails asynchronously
@shared_task
def send_event_email(event_id):
    # Retrieve the event instance using its ID
    event = Event.objects.get(id=event_id)
    
    # Prepare the email subject and message content
    subject = f"New Event Created: {event.title}"
    message = f"Event '{event.title}' is scheduled at {event.start_time}"
    
    # Send an email notification (dummy email address for example)
    send_mail(subject, message, 'noreply@example.com', ['recipient@example.com'])
