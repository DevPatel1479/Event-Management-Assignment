# 🎉 Event Management System (Django REST Framework)

A RESTful API built with **Django** and **Django REST Framework (DRF)** for managing events, RSVPs, and reviews.  

---

## 🚀 Features

- 👥 **User Profiles** – Extend Django’s User model with additional info.  
- 📅 **Event Management** – Create, update, delete, and view events.  
- 💌 **RSVP System** – Users can RSVP as “Going”, “Maybe”, or “Not Going”.  
- 📝 **Review System** – Users can leave reviews and ratings for events.  
- 🔐 **Permissions & Authentication** – Role-based access (organizer/invited/public).  
- ⚡ **Celery Integration** – Asynchronous email notifications for new events.  
- 📄 **Pagination** – Paginated event and review lists for better performance.  

---

## ⚙️ Setup Instructions

### 1️⃣ Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```
**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2️⃣ Clone the Repository

```bash
git clone https://github.com/DevPatel1479/Event-Management-Assignment
cd Event-Management-Assignment
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Apply Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5️⃣ Create Superuser (optional but recommended)
```bash
python manage.py createsuperuser
```

### 6️⃣ Run the Development Server
```bash
python manage.py runserver
```
Server will start at:
👉 http://127.0.0.1:8000/

Once the server starts, visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/)  
to view the JSON welcome message that lists all key API endpoints.

### 🧪 API Endpoint Testing Guide

This section helps you test each API step-by-step — from authentication to event, RSVP, and review management.

### 🔐 1️⃣ Obtain JWT Token (Authentication)

Endpoint:
```bash
POST /api/token/
```

Request Body:
```bash
{
  "username": "your_username",
  "password": "your_password"
}
```

Response:
```bash
{
  "refresh": "eyJhbGciOiJIUzI1NiIs...",
  "access": "eyJhbGciOiJIUzI1NiIs..."
}
```
✅ Save the access token — you’ll need it for all authenticated requests.


### 🎉 2️⃣ Event API

➕ Create a New Event

Endpoint: 
```bash
POST /api/events/
```

Headers:
```bash
Authorization: Bearer <your_access_token>
Content-Type: application/json
```

Request Body:
```bash
{
  "title": "AI Conference 2025",
  "description": "An event for AI enthusiasts and professionals.",
  "location": "Ahmedabad, India",
  "start_time": "2025-11-10T10:00:00Z",
  "end_time": "2025-11-10T17:00:00Z",
  "is_public": true,
  "invited_users" : [2] 
}

```
in above [2] is the user_id 

Response:
```bash
{
    "id": 5,
    "organizer": "dev",
    "title": "AI Conference 2025",
    "description": "An event for AI enthusiasts and professionals.",
    "location": "Ahmedabad, India",
    "start_time": "2025-11-10T10:00:00Z",
    "end_time": "2025-11-10T17:00:00Z",
    "is_public": true,
    "created_at": "2025-10-30T16:35:37.477766Z",
    "updated_at": "2025-10-30T16:35:37.477766Z",
    "invited_users": [
        2
    ]
}
```

### 📜 List All Events (public events only)

Endpoint:
```bash
GET /api/events/
```

Response:
```bash
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 5,
            "organizer": "dev",
            "title": "AI Conference 2025",
            "description": "An event for AI enthusiasts and professionals.",
            "location": "Ahmedabad, India",
            "start_time": "2025-11-10T10:00:00Z",
            "end_time": "2025-11-10T17:00:00Z",
            "is_public": true,
            "created_at": "2025-10-30T16:35:37.477766Z",
            "updated_at": "2025-10-30T16:35:37.477766Z",
            "invited_users": [
                2
            ]
        },
        {
            "id": 3,
            "organizer": "dev",
            "title": "Exam",
            "description": "python test",
            "location": "Online",
            "start_time": "2030-01-01T10:00:00Z",
            "end_time": "2030-01-01T12:00:00Z",
            "is_public": true,
            "created_at": "2025-10-29T17:14:08.000459Z",
            "updated_at": "2025-10-29T17:34:54.951821Z",
            "invited_users": []
        }
    ]
}
```

### 🔍 Get Event Details

Endpoint: 
```bash
GET /api/events/{id}/
```

### ✏️ Update Event (Organizer Only)

Endpoint:
```bash
PUT /api/events/{id}/
```

Headers:
```bash
Authorization: Bearer <your_access_token>
```

Request Body Example:
```bash
{
  "title": "AI Summit 2025",
  "description": "Updated description for AI summit.",
  "location" : "am",
  "start_time" : "2025-10-29T17:14:08.000459Z",
  "end_time" : "2025-10-29T17:34:54.951821Z"
}
```

Response:
```bash
{
    "id": 5,
    "organizer": "dev",
    "title": "AI Summit 2025",
    "description": "Updated description for AI summit.",
    "location": "am",
    "start_time": "2025-10-29T17:14:08.000459Z",
    "end_time": "2025-10-29T17:34:54.951821Z",
    "is_public": true,
    "created_at": "2025-10-30T16:35:37.477766Z",
    "updated_at": "2025-10-30T16:54:15.169843Z",
    "invited_users": [
        2
    ]
}
```

### ❌ Delete Event (Organizer Only)

Endpoint: 
```bash
DELETE /api/events/{id}/
```

### 📅 3️⃣ RSVP API

✅ RSVP to an Event

Endpoint: 
```bash
POST /api/events/{event_id}/rsvp/
```

Headers:
```bash
Authorization: Bearer <your_access_token>
Content-Type: application/json
```

Request Body:
```bash
{
  "status": "Going"  // or use any out of this  ("Going", "Maybe", "Not Going")
}
```

Response:
```bash
{
    "id": 3,
    "user": "dev",
    "event": 5,
    "status": "Maybe"
}
```

🔄 Update RSVP Status

Endpoint: 
```bash
PATCH /api/events/{event_id}/rsvp/{user_id}/
```
Request Body:
```bash
{
  "status": "Not Going"
}

```

Response:
```bash
{
    "id": 3,
    "user": "dev",
    "event": 5,
    "status": "Not Going"
}
```

📝 4️⃣ Review API

✍️ Add a Review for an Event

Endpoint: 
```bash
POST /api/events/{event_id}/reviews/
```

Headers:
```bash
Authorization: Bearer <your_access_token>
Content-Type: application/json
```

Request Body:
```bash
{
  "rating": 4,
  "comment": "Great event with insightful sessions!"
}
```

Response:
```bash
{
    "id": 2,
    "user": "dev",
    "rating": 4,
    "comment": "Great event with insightful sessions!",
    "created_at": "2025-10-30T17:04:49.745048Z",
    "event": 5
}
```

### 👀 List All Reviews for an Event

Endpoint: 
```bash
GET /api/events/{event_id}/reviews/
```

Response Example:
```bash
[
    {
        "id": 2,
        "user": "dev",
        "rating": 4,
        "comment": "Great event with insightful sessions!",
        "created_at": "2025-10-30T17:04:49.745048Z",
        "event": 5
    }
]
```

### 🧭 5️⃣ Token Refresh

Endpoint: 
```bash
POST /api/token/refresh/
```

Request Body:
```bash
{
  "refresh": "<your_refresh_token>"
}
```

Response:
```bash
{
  "access": "<new_access_token>"
}
```





