# Place Review REST API

A Django REST API for reviewing places (restaurants, shops, doctors, etc.) with user authentication, place management, and search functionality.

Video Walkthough - https://drive.google.com/file/d/1_lYXiHzC_2kW8Yp558VhqkH7rNWXTDq4/view?usp=sharing

## Features

- User registration and authentication with phone numbers
- Token-based authentication
- Add reviews for places (creates place if it doesn't exist)
- Search places by name and/or minimum rating
- View detailed place information with all reviews
- User's own review appears first in place details

## Assumptions

* **Search Functionality:** The requirements mentioned searching by "category". Since the data model requirements only specified Name and Address for a Place, I have assumed that searching by "Name" covers the intent of category search (e.g., searching for "Cafe" or "Doctor" will find places with those terms in their name).
* **Production Deployment:** As requested, the solution is designed to run with a simple web server and database setup, avoiding complex external search engines (like Elasticsearch) in favor of optimized SQL queries.

## Technology Stack

- Django 4.2.7
- Django REST Framework 3.14.0
- PostgreSQL (relational database)
- Token Authentication

## Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip

## Installation & Setup

### 1. Create PostgreSQL Database

```bash
# Login to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE place_review_db;

# Exit PostgreSQL
\q
```

### 2. Setup Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Database

Edit `config/settings.py` if your PostgreSQL credentials differ:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'place_review_db',
        'USER': 'postgres',        # Change if needed
        'PASSWORD': 'postgres',    # Change if needed
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 4. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Admin User (Optional)

```bash
python manage.py createsuperuser
# Follow prompts - use phone number format for username
```

### 6. Populate Sample Data

```bash
python populate_data.py
```

This creates:
- 50 sample users (password: `password123`)
- 100 sample places
- Random reviews (300-500 reviews)

### 7. Run Development Server

```bash
python manage.py runserver
```

API will be available at: `http://localhost:8000/api/`

## API Endpoints

### Authentication

#### Register User
```
POST /api/register/
Content-Type: application/json

{
    "name": "John Doe",
    "phone_number": "+1234567890",
    "password": "securepass123"
}

Response:
{
    "user": {
        "id": 1,
        "name": "John Doe",
        "phone_number": "+1234567890"
    },
    "token": "abc123token..."
}
```

#### Login User
```
POST /api/login/
Content-Type: application/json

{
    "phone_number": "+1234567890",
    "password": "securepass123"
}

Response:
{
    "user": {
        "id": 1,
        "name": "John Doe",
        "phone_number": "+1234567890"
    },
    "token": "abc123token..."
}
```

### Reviews

#### Add Review
```
POST /api/reviews/
Authorization: Token abc123token...
Content-Type: application/json

{
    "place_name": "Great Coffee Shop",
    "place_address": "123 Main St, City",
    "rating": 5,
    "text": "Amazing coffee and atmosphere!"
}

Response:
{
    "id": 1,
    "place": {
        "id": 1,
        "name": "Great Coffee Shop",
        "address": "123 Main St, City"
    },
    "rating": 5,
    "text": "Amazing coffee and atmosphere!",
    "created_at": "2024-12-26T10:30:00Z"
}
```

### Places

#### Search Places
```
GET /api/places/search/
Authorization: Token abc123token...

Query Parameters:
- name (optional): Search by place name (partial match)
- min_rating (optional): Filter by minimum average rating (1-5)

Examples:
/api/places/search/?name=coffee
/api/places/search/?min_rating=4.0
/api/places/search/?name=cafe&min_rating=4.5

Response:
[
    {
        "id": 1,
        "name": "Great Coffee Shop",
        "average_rating": 4.75
    },
    {
        "id": 2,
        "name": "Coffee Haven",
        "average_rating": 4.50
    }
]
```

#### Get Place Details
```
GET /api/places/{id}/
Authorization: Token abc123token...

Response:
{
    "id": 1,
    "name": "Great Coffee Shop",
    "address": "123 Main St, City",
    "average_rating": 4.75,
    "reviews": [
        {
            "id": 5,
            "rating": 5,
            "text": "My own review appears first!",
            "user_name": "John Doe",
            "created_at": "2024-12-26T10:30:00Z"
        },
        {
            "id": 3,
            "rating": 5,
            "text": "Excellent service!",
            "user_name": "Jane Smith",
            "created_at": "2024-12-25T14:20:00Z"
        }
    ]
}
```

## Testing the API

### Using Postman (Recommended)

A Postman collection (`place_review_api.postman_collection.json`) is included in the root directory.

1. Import the file into Postman.
2. Run the **Login** request first.
3. The collection is scripted to **automatically save the Auth Token**, so you can immediately run other requests (Search, Add Review) without manual copy-pasting.

### Using curl

```bash
# Register
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","phone_number":"+1111111111","password":"test123"}'

# Login (save the token)
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number":"+1111111111","password":"test123"}'

# Add review (use token from login)
curl -X POST http://localhost:8000/api/reviews/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"place_name":"Test Cafe","place_address":"456 Test St","rating":5,"text":"Great!"}'

# Search places
curl -X GET "http://localhost:8000/api/places/search/?name=cafe" \
  -H "Authorization: Token YOUR_TOKEN_HERE"

# Get place details
curl -X GET http://localhost:8000/api/places/1/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

## Project Structure

```
place_review_api/
├── config/
│   ├── __init__.py
│   ├── settings.py        # Django settings
│   ├── urls.py           # Main URL routing
│   └── wsgi.py
├── reviews/
│   ├── __init__.py
│   ├── models.py         # User, Place, Review models
│   ├── serializers.py    # REST serializers
│   ├── views.py          # API views
│   ├── urls.py           # App URL routing
│   ├── admin.py          # Django admin config
│   └── migrations/
├── manage.py
├── requirements.txt
├── populate_data.py      # Data population script
└── README.md
```

## Database Schema

### User
- id (PK)
- name
- phone_number (unique)
- password (hashed)
- created_at

### Place
- id (PK)
- name
- address
- created_at
- Unique constraint: (name, address)

### Review
- id (PK)
- user_id (FK)
- place_id (FK)
- rating (1-5)
- text
- created_at

## Key Implementation Details

1. **Authentication**: Token-based using Django REST Framework's TokenAuthentication
2. **User Model**: Custom user model with phone number as username
3. **Place Creation**: Places are created automatically when adding a review if they don't exist
4. **Search Logic**: 
   - Exact name matches appear first, then partial matches
   - Minimum rating filters by average rating
5. **Review Ordering**: Current user's review appears first, others sorted by newest
6. **Database**: PostgreSQL with proper indexes on frequently queried fields

## Production Considerations

Before deploying to production:

1. Change `SECRET_KEY` in settings.py
2. Set `DEBUG = False`
3. Configure `ALLOWED_HOSTS`
4. Use environment variables for sensitive data
5. Set up proper CORS headers if needed
6. Configure production database credentials
7. Set up static file serving
8. Use HTTPS
9. Implement rate limiting
10. Add comprehensive logging

## Notes

- All endpoints except register and login require authentication
- Phone numbers must be unique across users
- Each place has a unique combination of name and address
- Reviews are rated 1-5 stars
- Search is case-insensitive
- Average ratings are calculated on-the-fly
