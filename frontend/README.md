# StageLink — Frontend

A plain **HTML + CSS + JavaScript** frontend for the existing StageLink Django API.
No build step, no framework, no backend changes required to run it.

## Pages

| File | Purpose |
|------|---------|
| `login.html` | Sign in (entry point — `index.html` redirects here) |
| `register.html` | Registration (student / school / company, role-aware fields) |
| `verify.html` | Email verification with the 6-digit code |
| `reset-password.html` | Password recovery (request code → set new password) |
| `profile.html` | Role-based dashboard (`/me/`) |
| `planning.html` | List events that concern you, with edit / remove |
| `create-event.html` | Create an event (personal / group / team depending on role) |
| `edit-event.html` | Edit or delete an event you created |
| `groups-teams.html` | Schools manage groups, companies manage teams, students view theirs |

Shared code lives in `css/style.css` and `js/api.js`.

## Running it

The frontend talks to the Django API at `http://127.0.0.1:8000` (see `API_BASE` at the
top of `js/api.js` — change it if your server runs elsewhere).

Because the API uses **session cookies**, browsers are strict about cross-origin
cookies. The most reliable setup is to serve the frontend over `http://` (not the
`file://` protocol). From the `frontend/` folder:

```bash
# any static server works; for example:
python -m http.server 5500
```

Then open <http://127.0.0.1:5500/login.html>.

Start the Django backend separately as usual:

```bash
python manage.py runserver
```

## A note on CSRF (create / edit / delete actions)

The **auth and read** endpoints work out of the box:
register, verify, login, logout, reset/update password, and the
`GET` calls for `/me/`, `/groups/`, `/teams/`.

The **write** endpoints — `groups/create`, `teams/create`, `events/create`,
`events/<id>/edit`, `events/<id>/remove` — are protected by Django's CSRF
middleware. The frontend already sends the `X-CSRFToken` header read from the
`csrftoken` cookie (the standard Django pattern). For that cookie to exist, Django
just needs to issue it once. The smallest, optional one-line enabler (only if you
want these actions to work) is to mark a `GET` view with `@ensure_csrf_cookie`,
e.g. on `get_user` (`/api/v1/me/`):

```python
from django.views.decorators.csrf import ensure_csrf_cookie

@ensure_csrf_cookie   # add this line
@require_GET
def get_user(request):
    ...
```

This was left untouched per the "don't modify the backend" requirement — apply it
only if you want the create/edit/delete buttons to succeed without other changes.
