from django.contrib import admin
from .models import Department, Team, TeamMember, Task


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

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "team",
        "user",
        "team_role",
        "member_type",
        "joined_at",
        "is_active",
        "created_at",
        "updated_at",
        "deleted_at",
    )
    list_filter = ("team_role", "member_type", "is_active", "created_at", "deleted_at")
    search_fields = ("team__name", "user__name", "user__email")
    readonly_fields = ("created_at", "updated_at", "deleted_at")


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "team",
        "assigned_to",
        "assigned_by",
        "status",
        "priority",
        "due_date",
        "completed_at",
        "created_at",
        "updated_at",
        "deleted_at",
    )
    list_filter = ("status", "priority", "team", "created_at", "deleted_at")
    search_fields = (
        "title",
        "description",
        "team__name",
        "assigned_to__name",
        "assigned_by__name",
    )
    readonly_fields = ("created_at", "updated_at", "deleted_at", "completed_at")