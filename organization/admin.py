from django.contrib import admin

from .models import Department, Team


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "supervisor",
        "is_active",
        "created_at",
        "updated_at",
        "deleted_at",
    )
    list_filter = ("is_active", "created_at", "deleted_at")
    search_fields = ("name", "description", "supervisor__name", "supervisor__email")
    readonly_fields = ("created_at", "updated_at", "deleted_at")


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "department",
        "leader",
        "assistant_leader",
        "created_at",
        "updated_at",
        "deleted_at",
    )
    list_filter = ("department", "created_at", "deleted_at")
    search_fields = (
        "name",
        "description",
        "department__name",
        "leader__name",
        "leader__email",
        "assistant_leader__name",
        "assistant_leader__email",
    )
    readonly_fields = ("created_at", "updated_at", "deleted_at")