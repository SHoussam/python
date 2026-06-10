from .user_controle import verify_user , registration, login, logout, get_user, reset_password, update_password
from django.urls import path

x = "api/v1"
urlpatterns = [
    path(f"{x}/register/", registration, name="register"),
    path(f"{x}/verify/", verify_user, name="verify_user"),
    path(f"{x}/login/", login, name="login"),
    path(f"{x}/logout/", logout, name="logout"),
    path(f"{x}/user/", get_user, name="get_user"),
    path(f"{x}/reset-password/", reset_password, name="reset_password"),
    path(f"{x}/update-password/", update_password, name="update_password"),
]