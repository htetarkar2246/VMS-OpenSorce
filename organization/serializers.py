from rest_framework import serializers

from .models import Department, Team


class DepartmentSerializer(serializers.ModelSerializer):
    supervisor_name = serializers.CharField(source="supervisor.name", read_only=True)

    class Meta:
        model = Department
        fields = [
            "id",
            "name",
            "description",
            "supervisor",
            "supervisor_name",
            "is_active",
            "created_at",
            "updated_at",
            "deleted_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "deleted_at",
            "supervisor_name",
        ]


class TeamSerializer(serializers.ModelSerializer):
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