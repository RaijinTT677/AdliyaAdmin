from django.contrib import admin
from .models import Content

@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ('name', 'format', 'is_active', 'views')
    list_filter = ('format', 'is_active')
    search_fields = ('name',)
