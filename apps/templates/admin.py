from django.contrib import admin

from apps.templates.models import Template, UserTemplate


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "is_premium", "is_active", "usage_count", "created_at"]
    list_filter = ["category", "is_premium", "is_active"]
    search_fields = ["name", "description"]


@admin.register(UserTemplate)
class UserTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "is_default", "created_at"]
    list_filter = ["is_default", "created_at"]
    search_fields = ["name", "user__email"]
