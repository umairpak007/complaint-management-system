from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def analytics_dashboard(request):
    return render(request, 'analytics/dashboard.html')

# Basic placeholder views
@login_required
def revenue_report(request):
    return render(request, 'analytics/revenue_report.html')

@login_required
def engineer_performance(request):
    return render(request, 'analytics/engineer_performance.html')

@login_required
def parts_usage_report(request):
    return render(request, 'analytics/parts_usage.html')

@login_required
def export_pdf(request):
    return render(request, 'analytics/export_reports.html')

@login_required
def export_excel(request):
    return render(request, 'analytics/export_reports.html')

@login_required
def complaint_trends(request):
    return render(request, 'analytics/charts.html')