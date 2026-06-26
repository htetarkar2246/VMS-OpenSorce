"""Serializer layer for organization and collaboration endpoints."""

from rest_framework import serializers

from .models import (
    Achievement,
    Department,
    Meeting,
    MeetingAttendee,
    Task,
    Team,
    TeamMember,
)


class DepartmentSerializer(serializers.ModelSerializer):
    """Expose department details with human-readable staff names."""

    supervisor_name = serializers.CharField(source="supervisor.name", read_only=True)
    coordinator_name = serializers.CharField(source="coordinator.name", read_only=True)

    class Meta:
        model = Department
        fields = [
            "id",
            "name",
            "description",
            "supervisor",
            "supervisor_name",
            "coordinator",
            "coordinator_name",
            "is_active",
            "created_at",
            "updated_at",
            "deleted_at",
        ]
        read_only_fields = [
            "id",
            "supervisor_name",
            "coordinator_name",
            "created_at",
            "updated_at",
            "deleted_at",
        ]


class TeamSerializer(serializers.ModelSerializer):
    """Expose team details with related department and lead names."""

    department_name = serializers.CharField(source="department.name", read_only=True)
    leader_name = serializers.CharField(source="leader.name", read_only=True)
    assistant_leader_name = serializers.CharField(
        source="assistant_leader.name",
        read_only=True,
    )

    class Meta:
        model = Team
        fields = [
            "id",
            "department",
            "department_name",
            "name",
            "description",
            "leader",
            "leader_name",
            "assistant_leader",
            "assistant_leader_name",
            "created_at",
            "updated_at",
            "deleted_at",
        ]
        read_only_fields = [
            "id",
            "department_name",
            "leader_name",
            "assistant_leader_name",
            "created_at",
            "updated_at",
            "deleted_at",
        ]


class TeamMemberSerializer(serializers.ModelSerializer):
    """Serialize team membership assignments with friendly display fields."""

    user_name = serializers.CharField(source="user.name", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)
    team_name = serializers.CharField(source="team.name", read_only=True)

    class Meta:
        model = TeamMember
        fields = [
            "id",
            "team",
            "team_name",
            "user",
            "user_name",
            "user_email",
            "team_role",
            "member_type",
            "joined_at",
            "is_active",
            "created_at",
            "updated_at",
            "deleted_at",
        ]
        read_only_fields = [
            "id",
            "team_name",
            "user_name",
            "user_email",
            "created_at",
            "updated_at",
            "deleted_at",
        ]


class TaskSerializer(serializers.ModelSerializer):
    """Serialize tasks with team and assignment context."""

    team_name = serializers.CharField(source="team.name", read_only=True)
    assigned_to_name = serializers.CharField(source="assigned_to.name", read_only=True)
    assigned_by_name = serializers.CharField(source="assigned_by.name", read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "team",
            "team_name",
            "assigned_to",
            "assigned_to_name",
            "assigned_by",
            "assigned_by_name",
            "title",
            "description",
            "status",
            "priority",
            "due_date",
            "completed_at",
            "created_at",
            "updated_at",
            "deleted_at",
        ]
        read_only_fields = [
            "id",
            "team_name",
            "assigned_to_name",
            "assigned_by",
            "assigned_by_name",
            "completed_at",
            "created_at",
            "updated_at",
            "deleted_at",
        ]


class AchievementSerializer(serializers.ModelSerializer):
    """Serialize achievements with related user and team labels."""

    user_name = serializers.CharField(source="user.name", read_only=True)
    team_name = serializers.CharField(source="team.name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.name", read_only=True)

    class Meta:
        model = Achievement
        fields = [
            "id",
            "user",
            "user_name",
            "team",
            "team_name",
            "title",
            "description",
            "achievement_date",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
            "deleted_at",
        ]
        read_only_fields = [
            "id",
            "user_name",
            "team_name",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
            "deleted_at",
        ]


class MeetingAttendeeSerializer(serializers.ModelSerializer):
    """Serialize attendee records with user-friendly identity fields."""

    user_name = serializers.CharField(source="user.name", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = MeetingAttendee
        fields = [
            "id",
            "meeting",
            "user",
            "user_name",
            "user_email",
            "status",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user_name", "user_email", "created_at", "updated_at"]


class MeetingSerializer(serializers.ModelSerializer):
    """Serialize meetings together with nested attendees."""

    department_name = serializers.CharField(source="department.name", read_only=True)
    team_name = serializers.CharField(source="team.name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.name", read_only=True)
    attendees = MeetingAttendeeSerializer(many=True, read_only=True)

    class Meta:
        model = Meeting
        fields = [
            "id",
            "title",
            "description",
            "meeting_type",
            "department",
            "department_name",
            "team",
            "team_name",
            "created_by",
            "created_by_name",
            "start_datetime",
            "end_datetime",
            "location",
            "google_event_id",
            "google_calendar_link",
            "is_synced_google",
            "attendees",
            "created_at",
            "updated_at",
            "deleted_at",
        ]
        read_only_fields = [
            "id",
            "department_name",
            "team_name",
            "created_by",
            "created_by_name",
            "google_event_id",
            "google_calendar_link",
            "is_synced_google",
            "created_at",
            "updated_at",
            "deleted_at",
        ]
