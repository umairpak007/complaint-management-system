#this is urls.py for analytics app
from django.urls import path
from . import views

urlpatterns = [
    path('', views.analytics_dashboard, name='analytics_dashboard'),
    path('reports/revenue/', views.revenue_report, name='revenue_report'),
    path('reports/engineer-performance/', views.engineer_performance, name='engineer_performance'),
    path('reports/parts-usage/', views.parts_usage_report, name='parts_usage_report'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
    path('export/excel/', views.export_excel, name='export_excel'),
    path('charts/complaint-trends/', views.complaint_trends, name='complaint_trends'),
]