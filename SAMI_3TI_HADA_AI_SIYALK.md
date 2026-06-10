# StageLink API Documentation

## Overview

StageLink is a collaborative platform connecting Students, Schools, and Companies.

Authentication is session-based. After login, the backend stores:

```python
request.session["user"] = {
    "id": user.id,
    "role": user.role
}
```

Most protected endpoints require a valid session.

---

# Roles

Possible roles:

```text
student
school
company
```

---

# User Registration

## POST /api/v1/register/

### Request

```json
{
  "role": "student",
  "first_name": "Houssam",
  "last_name": "Yoka",
  "email": "houssam@example.com",
  "password": "password123",
  "confirm_password": "password123",
  "group_id": 1,
  "team_id": 1
}
```

### Notes

Student:

* group_id is required
* team_id is optional

School:

```json
{
  "role": "school",
  "school_name": "EMSI Tanger"
}
```

Company:

```json
{
  "role": "company",
  "company_name": "Capgemini"
}
```

---

# Verify Account

## POST /api/v1/verify/

### Request

```json
{
  "email": "user@example.com",
  "code": "123456"
}
```

---

# Login

## POST /api/v1/login/

### Request

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

Creates a server session.

---

# Logout

## POST /api/v1/logout/

Destroys the current session.

---

# Reset Password

## POST /api/v1/reset-password/

### Request

```json
{
  "email": "user@example.com"
}
```

Sends a verification code.

---

# Update Password

## POST /api/v1/update-password/

### Request

```json
{
  "email": "user@example.com",
  "code": "123456",
  "new_password": "newpass",
  "confirm_password": "newpass"
}
```

---

# Current User

## GET /api/v1/me/

Returns the connected user's complete profile.

Student response example:

```json
{
  "id": 1,
  "first_name": "Houssam",
  "last_name": "Yoka",
  "email": "houssam@example.com",
  "role": "student",

  "group": {
    "id": 1,
    "name": "Group 4"
  },

  "team": {
    "id": 2,
    "name": "Backend Team"
  },

  "school": {
    "id": 1,
    "name": "EMSI"
  },

  "company": {
    "id": 1,
    "name": "Capgemini"
  },

  "events": []
}
```

---

# Groups

## GET /api/v1/groups/

Returns all groups.

Example:

```json
{
  "groups": [
    {
      "id": 1,
      "name": "Group 4",
      "year": "3IIR",
      "school": {
        "id": 1,
        "name": "EMSI"
      },
      "students": [
        {
          "id": 3,
          "name": "John Doe"
        }
      ]
    }
  ]
}
```

---

## POST /api/v1/groups/create/

Only schools can create groups.

### Request

```json
{
  "name": "Group 5",
  "year": "3IIR"
}
```

---

# Teams

## GET /api/v1/teams/

Returns all teams.

Example:

```json
{
  "teams": [
    {
      "id": 1,
      "name": "Backend Team",
      "company": {
        "id": 1,
        "name": "Capgemini"
      },
      "students": []
    }
  ]
}
```

---

## POST /api/v1/teams/create/

Only companies can create teams.

### Request

```json
{
  "name": "Frontend Team"
}
```

---

# Events

## POST /api/v1/events/create/

Creates events.

Student:

* creates a personal event

School:

* can create the same event for one or more groups

Company:

* can create the same event for one or more teams

### Request

```json
{
  "title": "Sprint Review",
  "description": "Weekly review",
  "start_date": "2026-06-15T10:00:00",
  "end_date": "2026-06-15T11:00:00",
  "group_ids": [1, 2]
}
```

or

```json
{
  "title": "Interview Session",
  "description": "Technical interview",
  "start_date": "2026-06-15T10:00:00",
  "end_date": "2026-06-15T11:00:00",
  "team_ids": [1, 2]
}
```

---

## POST /api/v1/events/{event_id}/edit/

Updates an event.

Only the creator can edit.

Example:

```json
{
  "title": "Updated Event Title",
  "description": "Updated description"
}
```

---

## POST /api/v1/events/{event_id}/remove/

Deletes an event.

Only the creator can delete.

---

# Main Relationships

Student:

```text
Student
 ├── User
 ├── Group (optional)
 └── Team (optional)
```

Group:

```text
School
 └── Groups
      └── Students
```

Team:

```text
Company
 └── Teams
      └── Students
```

Event:

```text
Event
 ├── Creator
 ├── Group (optional)
 ├── Team (optional)
 └── Participants (optional)
```

---

# Frontend Flow

1. Login
2. Call GET /api/v1/me/
3. Store user data
4. Build UI based on role

Student:

* Dashboard
* Personal events
* Group events
* Team events

School:

* Groups
* Students
* Group events

Company:

* Teams
* Interns
* Team events
