# Book Recommendation API

A RESTful API for book metadata, ratings, and recommendations, developed for XJCO3011 Coursework 1 at the University of Leeds.

## Features

- Full CRUD operations for Books and Reviews
- Search books by title or author
- Filter books by publication year
- Top-rated books ranking endpoint
- Author statistics and aggregation endpoint
- Auto-generated interactive API documentation (Swagger UI)

## Tech Stack

- **Framework:** Django 5.2 + Django REST Framework 3.17
- **Database:** SQLite
- **Documentation:** drf-spectacular (OpenAPI 3.0 / Swagger UI)
- **Dataset:** Goodreads Books Dataset (Kaggle)

## Setup Instructions

1. Clone the repository and enter the project folder.

2. Create and activate a conda environment:

    conda create -n bookapi_env python=3.11 -y
    conda activate bookapi_env

3. Install dependencies:

    pip install django djangorestframework django-filter drf-spectacular

4. Run database migrations:

    python manage.py migrate

5. Create a superuser for Admin panel access:

    python manage.py createsuperuser

6. Start the development server:

    python manage.py runserver

## API Endpoints

| Method     | Endpoint                    | Description                        |
|------------|-----------------------------|------------------------------------|
| GET        | /api/books/                 | List all books (search and filter) |
| POST       | /api/books/                 | Create a new book                  |
| GET        | /api/books/{id}/            | Retrieve a specific book           |
| PUT/PATCH  | /api/books/{id}/            | Update a book                      |
| DELETE     | /api/books/{id}/            | Delete a book                      |
| GET        | /api/books/top-rated/       | Get top-rated books                |
| GET        | /api/books/author-stats/    | Get author statistics              |
| GET/POST   | /api/books/{id}/reviews/    | List or add reviews for a book     |
| GET/PUT/DELETE | /api/reviews/{id}/      | Manage a specific review           |

## API Documentation

Full interactive API documentation is available via Swagger UI at:
http://127.0.0.1:8000/api/docs/

A PDF version of the API documentation is included in this repository: API_Documentation.pdf

## Admin Panel

Access the Django Admin panel at http://127.0.0.1:8000/admin/ using your superuser credentials.
