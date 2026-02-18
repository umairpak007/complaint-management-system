from django.contrib import admin
from .models import Part

@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ('name', 'make', 'model', 'source', 'is_active')
    list_filter = ('source', 'is_active')
    search_fields = ('name', 'make', 'model')
    