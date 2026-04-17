# TeamFlow Backend

TeamFlow Backend is the API service for the TeamFlow project management system. It provides authentication, task management, Kanban board persistence, and deadline-related features for the frontend application.

## Features

- User registration and login
- JWT authentication
- Get current user info (`/auth/me`)
- Task CRUD
- Task reorder API for Kanban board
- Assignee support
- Deadline and estimated days management
- Completed time tracking

## Tech Stack

- FastAPI
- SQLAlchemy
- PostgreSQL
- python-jose
- passlib + bcrypt
- Uvicorn

## Main API Routes

### Auth
- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`

### Users
- `GET /users`

### Tasks
- `GET /tasks`
- `POST /tasks`
- `PUT /tasks/{task_id}`
- `PUT /tasks/reorder`
- `DELETE /tasks/{task_id}`

## Database Overview

### users
- `id`
- `name`
- `email`
- `password_hash`
- `color`

### tasks
- `id`
- `title`
- `description`
- `status`
- `category`
- `position`
- `assignee_id`
- `created_by`
- `deadline`
- `estimated_days`
- `completed_at`
- `created_at`
- `updated_at`

## Run Locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload