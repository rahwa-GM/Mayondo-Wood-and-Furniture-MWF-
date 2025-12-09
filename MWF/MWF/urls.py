"""
URL configuration for MWF project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin # Import Django's admin module
# path: used to define individual routes
#include: to include URLs from other apps
from django.urls import path, include 

urlpatterns = [
    # Django admin
    path("admin/", admin.site.urls),

    # User authentication and profiles
    path("", include("accounts.urls")),  # namespace comes from accounts/urls.py

    # Inventory management
    path("inventory/", include("inventory.urls")),

    # Sales management
    path("sales/", include("sales.urls")),

    # Staff management
    path("staff/", include("staff.urls")),
]
