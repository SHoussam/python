from django.urls import path 

from . import views


app_name = "webterminal"

urlpatterns = [
    path("", views.index, name="index"),
    path("app/login/", views.login_view, name="login"),
    path("app/login/submit/", views.login_submit, name="login_submit"),
    path("app/register/", views.register_view, name="register"),
    path("app/register/submit/", views.register_submit, name="register_submit"),
    path("app/verify-email/", views.verify_email_view, name="verify_email"),
    path("app/verify-email/submit/", views.verify_email_submit, name="verify_email_submit"),
    path("app/dashboard/", views.dashboard, name="dashboard"),
    path("app/logout/", views.logout_view, name="logout"),
    path("app/admin/verify/", views.verify_entreprise, name="verify_entreprise"),
    path("app/events/create/", views.create_event, name="create_event"),
    path("app/events/edit/<int:event_id>/", views.edit_event, name="edit_event"),
    path( "app/events/update/<int:event_id>/", views.update_event, name="update_event"),
    path("app/event/", views.event, name="event"),

]
