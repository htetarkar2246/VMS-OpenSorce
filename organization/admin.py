from django.contrib import admin
from .models import Achievement, Department, Meeting, MeetingAttendee, Task, Team, TeamMember

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "supervisor",
        "coordinator",
        "is_active",
        "created_at",
        "updated_at",
        "deleted_at",
    )
    list_filter = ("is_active", "created_at", "deleted_at")
    search_fields = (
        "name",
        "description",
        "supervisor__name",
        "supervisor__email",
        "coordinator__name",
        "coordinator__email",
    )
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

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "user",
        "team",
        "achievement_date",
        "created_by",
        "created_at",
        "updated_at",
        "deleted_at",
    )
    list_filter = ("team", "achievement_date", "created_at", "deleted_at")
    search_fields = ("title", "description", "user__name", "team__name")
    readonly_fields = ("created_at", "updated_at", "deleted_at")


class MeetingAttendeeInline(admin.TabularInline):
    model = MeetingAttendee
    extra = 1


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    inlines = [MeetingAttendeeInline]

    list_display = (
        "id",
        "title",
        "meeting_type",
        "department",
        "team",
        "start_datetime",
        "end_datetime",
        "created_by",
        "is_synced_google",
        "created_at",
        "updated_at",
        "deleted_at",
    )
    list_filter = ("meeting_type", "department", "team", "is_synced_google", "created_at", "deleted_at")
    search_fields = ("title", "description", "location", "department__name", "team__name")
    readonly_fields = (
        "google_event_id",
        "google_calendar_link",
        "is_synced_google",
        "created_at",
        "updated_at",
        "deleted_at",
    )


@admin.register(MeetingAttendee)
class MeetingAttendeeAdmin(admin.ModelAdmin):
    list_display = ("id", "meeting", "user", "status", "created_at", "updated_at")
    list_filter = ("status", "created_at")
    search_fields = ("meeting__title", "user__name", "user__email")
    readonly_fields = ("created_at", "updated_at")
