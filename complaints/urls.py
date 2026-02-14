
from django.urls import path
from . import views

urlpatterns = [
    path('', views.complaint_list, name='complaint_list'),
    path('<int:pk>/assign/', views.assign_complaint, name='assign_complaint'),
]
