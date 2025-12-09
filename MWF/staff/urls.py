from django.urls import path # Import the path function to define URL routes for this app
from . import views # Import views from the current app to connect URL patterns with view functions

# Namespace tells Django all the URL names inside this file belong to this app
app_name = 'staff' 

urlpatterns = [
    # List all staff members
    path('list/', views.list_staff, name='list'),

    # Add a new staff record
    path('add/', views.add_staff, name='add'),

    # Edit staff details (pk = primary key of the staff)
    path('update/<int:pk>/', views.update_staff, name='update'),

    # Delete staff profiles (pk = primary key of the staff)
    path('delete/<int:pk>/', views.delete_staff, name='delete'),
]

