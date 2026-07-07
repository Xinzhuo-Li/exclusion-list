from django.contrib import admin

from .models import DataSource, ExclusionRecord


@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "contributor", "record_count", "last_merged_at")
    search_fields = ("code", "name", "contributor")
