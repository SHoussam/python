from .user_controle import verify_user , registration, login, logout, get_user, reset_password, update_password
from .tg_controler import get_groups, get_teams,create_team, create_group
from .event_controler import create_event , edit_event, remove_event
from django.urls import path
x = "api/v1"
urlpatterns = [
  

    # Authentication
    path(f"{x}/register/", registration),
    path(f"{x}/verify/", verify_user),
    path(f"{x}/login/", login),
    path(f"{x}/logout/", logout),
    path(f"{x}/me/", get_user),

    # Password
    path(f"{x}/reset-password/", reset_password),
    path(f"{x}/update-password/", update_password),

    # Groups
    path(f"{x}/groups/", get_groups),
    path(f"{x}/groups/create/", create_group),

    # Teams
    path(f"{x}/teams/", get_teams),
    path(f"{x}/teams/create/", create_team),
    
    # Events
    path(f"{x}/events/create/", create_event),
    path(f"{x}/events/<int:event_id>/edit/", edit_event),
    path(f"{x}/events/<int:event_id>/remove/", remove_event),

]
