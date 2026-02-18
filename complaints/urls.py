# from django.urls import path
# from . import views

# urlpatterns = [
#     # Admin / Management URLs (Existing)
#     path('', views.complaint_list, name='complaint_list'),
#     path('<int:pk>/assign/', views.assign_complaint, name='assign_complaint'),
    
#     # Engineer Portal URLs
#     path('engineer/dashboard/', views.engineer_dashboard, name='engineer_dashboard'),
#     path('engineer/complaint/<int:pk>/', views.engineer_complaint_detail, name='engineer_complaint_detail'),
#     path('engineer/complaint/<int:pk>/resolve/', views.resolve_complaint, name='resolve_complaint'),
#     path('engineer/complaint/<int:pk>/status/', views.update_complaint_status, name='update_complaint_status'),
    
#     # AJAX URLs
#     path('ajax/calculate-part-cost/', views.calculate_part_cost_ajax, name='calculate_part_cost_ajax'),
    
# ]
from django.urls import path
from . import views

urlpatterns = [
    # Engineer Portal URLs (Specific - Pehle yeh)
    path('engineer/dashboard/', views.engineer_dashboard, name='engineer_dashboard'),
    path('engineer/complaint/<int:pk>/', views.engineer_complaint_detail, name='engineer_complaint_detail'),
    path('engineer/complaint/<int:pk>/resolve/', views.resolve_complaint, name='resolve_complaint'),
    path('engineer/complaint/<int:pk>/status/', views.update_complaint_status, name='update_complaint_status'),
    
    # AJAX URLs
    path('ajax/calculate-part-cost/', views.calculate_part_cost_ajax, name='calculate_part_cost_ajax'),
    
    # Admin / Management URLs (Generic - Baad mein yeh)
    path('', views.complaint_list, name='complaint_list'),
    path('<int:pk>/assign/', views.assign_complaint, name='assign_complaint'),
]
