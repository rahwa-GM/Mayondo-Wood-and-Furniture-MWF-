from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    # Sales URLS
    path("customer/add/", views.add_customer, name="add_customer"),
    path("customer/list/", views.list_customer, name="list_customer"),
    path("customer/update/<int:pk>/", views.update_customer, name="update_customer"),
    path("customer/delete/<int:pk>/", views.delete_customer, name="delete_customer"),
    
    
    path('sale/add/', views.add_sale, name='add_sale'),
    path('sale/list/', views.list_sale, name='list_sale'),
    path('sale/update/<int:pk>/', views.update_sale, name='update_sale'),
    path('sale/delete/<int:pk>/', views.delete_sale, name='delete_sale'),

    path('generate-report/', views.generate_sales_report, name='generate_sales_report'),
]
