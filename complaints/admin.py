from django.contrib import admin
from .models import Complaint, ComplaintAssignment, ComplaintPartIssue, Fault

# =========================
# Complaint Part Issue Inline
# =========================
class ComplaintPartIssueInline(admin.TabularInline):
    model = ComplaintPartIssue
    extra = 1
    fields = ('part', 'source', 'quantity', 'notes', 'issued_at')
    readonly_fields = ('issued_at',)


# =========================
# Complaint Assignment Admin
# =========================
@admin.register(ComplaintAssignment)
class ComplaintAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        'complaint', 
        'engineer', 
        'assigned_at', 
        'is_active',
        'parts_count'
    )
    list_filter = ('is_active', 'assigned_at')
    search_fields = (
        'complaint__complaint_no', 
        'engineer__username', 
        'remarks'
    )
    readonly_fields = ('assigned_at',)
    inlines = [ComplaintPartIssueInline]
    
    def parts_count(self, obj):
        return obj.issued_parts.count()
    parts_count.short_description = 'Parts'


# =========================
# Complaint Part Issue Admin
# =========================
@admin.register(ComplaintPartIssue)
class ComplaintPartIssueAdmin(admin.ModelAdmin):
    list_display = (
        'part', 
        'source',           
        'quantity', 
        'assignment', 
        'issued_at'
    )
    list_filter = ('source', 'issued_at')
    search_fields = (
        'part__name', 
        'source',
        'assignment__complaint__complaint_no'
    )
    readonly_fields = ('issued_at',)


# =========================
# Complaint Admin
# =========================
@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = (
        'complaint_no', 
        'client', 
        'product', 
        'status', 
        'priority'
    )
    list_filter = ('status', 'priority')
    search_fields = (
        'complaint_no', 
        'client__name', 
        'product__name'
    )
    readonly_fields = ('complaint_no', 'created_at', 'updated_at')


# =========================
# Fault Admin
# =========================
@admin.register(Fault)
class FaultAdmin(admin.ModelAdmin):
    list_display = ('fault_name', 'is_active')
    search_fields = ('fault_name',)