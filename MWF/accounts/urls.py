from django.urls import path
from . import views

# Namespace tells Django all the URL names inside this file belong to this app
app_name = 'accounts'

urlpatterns = [
    path("", views.login_user, name='login'),  # login is now homepage
    path("logout/", views.logout_user, name='logout'),
    path("manager/", views.dashboard_manager, name='dashboard_manager'),
    path("agent/", views.dashboard_agent, name='dashboard_agent'),
]

