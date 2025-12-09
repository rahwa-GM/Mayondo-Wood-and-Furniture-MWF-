from django.urls import path # Import the path function to define URL routes for this app
from . import views # Import views from the current app to connect URL patterns with view functions

# Namespace tells Django all the URL names inside this file belong to this app
app_name = 'inventory' 

urlpatterns = [
    # SUPPLIER URLS
    # Add a new supplier
    path("supplier/add/", views.add_supplier, name="add_supplier"),

    # List all suppliers
    path("supplier/list/", views.list_supplier, name="list_supplier"),

    # Edit supplier details (pk = primary key of the supplier)
    path("supplier/update/<int:pk>/", views.update_supplier, name="update_supplier"),

    # Delete supplier profiles (pk = primary key of the supplier)
    path("supplier/delete/<int:pk>/", views.delete_supplier, name="delete_supplier"),

    # PRODUCT URLS
    path("product/add/", views.add_product, name="add_product"),
    path("product/list/", views.list_product, name="list_product"),
    path("product/update/<int:pk>/", views.update_product, name="update_product"),
    path("product/delete/<int:pk>/", views.delete_product, name="delete_product"),

    # STOCK URLS
    path("stock/add/", views.add_stock, name="add_stock"),
    path("stock/list/", views.list_stock, name="list_stock"),
    path("stock/update/<int:pk>/", views.update_stock, name="update_stock"),
    path("stock/delete/<int:pk>/", views.delete_stock, name="delete_stock"),

    path('generate-stock-report/', views.generate_stock_report, name='generate_stock_report'),

]

