# this is urls for operations app
from django.urls import path
from . import views

urlpatterns = [
    path('', views.operations_dashboard, name='operations_dashboard'),
    path('user', views.user_management, name='user_management'),
    path('products/', views.product_management, name='product_management'),
    path('parts/', views.part_management, name='part_management'),
    path('pending/', views.pending_complaints, name='pending_complaints'),
    path('inventory/alerts/', views.inventory_alerts, name='inventory_alerts'),
    path('quick-actions/', views.quick_actions, name='quick_actions'),
]
