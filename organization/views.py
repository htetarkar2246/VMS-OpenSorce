from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import permissions, status, viewsets

from authentication.serializers import UserSerializer
from utils.permissions import (
    IsManagerOrReadOnly,
    IsManagerOrSupervisorOrReadOnly,
    IsManagerSupervisorLeaderOrReadOnly,
)
from utils.responses import error_response, success_response

from .models import (
    Achievement,
    Department,
    Meeting,
    MeetingAttendee,
    Task,
    Team,
    TeamMember,
)
from .serializers import (
    AchievementSerializer,
    DepartmentSerializer,
    MeetingAttendeeSerializer,
    MeetingSerializer,
    TaskSerializer,
    TeamMemberSerializer,
    TeamSerializer,
)

User = get_user_model()

class DepartmentViewSet(viewsets.ModelViewSet):
    serializer_class = DepartmentSerializer
    permission_classes = [IsManagerOrReadOnly]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Department.objects.none()

        user = self.request.user
        queryset = Department.objects.filter(deleted_at__isnull=True)

        if user.is_superuser or user.role == "MANAGER":
            return queryset

        if user.role == "SUPERVISOR":
            return queryset.filter(Q(supervisor=user) | Q(coordinator=user))

        return Department.objects.none()

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return success_response("Departments retrieved successfully.", serializer.data)

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return success_response("Department retrieved successfully.", serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return error_response(
                message="Validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()

        return success_response(
            message="Department created successfully.",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)

        serializer = self.get_serializer(
            self.get_object(),
            data=request.data,
            partial=partial,
        )

        if not serializer.is_valid():
            return error_response(
                message="Validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()

        return success_response("Department updated successfully.", serializer.data)

    def destroy(self, request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.role == "MANAGER"):
            return error_response(
                message="Only managers can delete departments.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        department = self.get_object()
        department.soft_delete()

        return success_response(message="Department deleted successfully.")


class TeamViewSet(viewsets.ModelViewSet):
    serializer_class = TeamSerializer
    permission_classes = [IsManagerOrSupervisorOrReadOnly]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Team.objects.none()

        user = self.request.user

        queryset = Team.objects.filter(deleted_at__isnull=True).select_related(
            "department",
            "leader",
            "assistant_leader",
        )

        if user.is_superuser or user.role == "MANAGER":
            return queryset

        if user.role == "SUPERVISOR":
            return queryset.filter(
                Q(department__supervisor=user) | Q(department__coordinator=user)
            )

        if user.role == "LEADER":
            return queryset.filter(Q(leader=user) | Q(assistant_leader=user))

        if user.role == "MEMBER":
            return queryset.filter(
                memberships__user=user,
                memberships__is_active=True,
                memberships__deleted_at__isnull=True,
            ).distinct()

        return Team.objects.none()

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return success_response("Teams retrieved successfully.", serializer.data)

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return success_response("Team retrieved successfully.", serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return error_response(
                message="Validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()

        return success_response(
            message="Team created successfully.",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        team = self.get_object()

        serializer = self.get_serializer(team, data=request.data, partial=partial)

        if not serializer.is_valid():
            return error_response(
                message="Validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if request.user.role == "SUPERVISOR" and not request.user.is_superuser:
            new_department = serializer.validated_data.get("department", team.department)

            if (
                new_department.supervisor_id != request.user.id
                and new_department.coordinator_id != request.user.id
            ):
                return error_response(
                    message="You can only assign teams to your own department.",
                    status_code=status.HTTP_403_FORBIDDEN,
                )

        serializer.save()

        return success_response("Team updated successfully.", serializer.data)

    def destroy(self, request, *args, **kwargs):
        if not (
            request.user.is_superuser
            or request.user.role in ["MANAGER", "SUPERVISOR"]
        ):
            return error_response(
                message="Only managers or supervisors can delete teams.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        team = self.get_object()
        team.soft_delete()

        return success_response(message="Team deleted successfully.")


class TeamMemberViewSet(viewsets.ModelViewSet):
    serializer_class = TeamMemberSerializer
    permission_classes = [IsManagerOrSupervisorOrReadOnly]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return TeamMember.objects.none()

        user = self.request.user

        queryset = TeamMember.objects.filter(deleted_at__isnull=True).select_related(
            "team",
            "team__department",
            "user",
        )

        if user.is_superuser or user.role == "MANAGER":
            return queryset

        if user.role == "SUPERVISOR":
            return queryset.filter(
                Q(team__department__supervisor=user)
                | Q(team__department__coordinator=user)
            )

        if user.role == "LEADER":
            return queryset.filter(
                Q(team__leader=user) | Q(team__assistant_leader=user)
            )

        if user.role == "MEMBER":
            return queryset.filter(user=user)

        return TeamMember.objects.none()

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return success_response("Team members retrieved successfully.", serializer.data)

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return success_response("Team member retrieved successfully.", serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return error_response(
                message="Validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()

        return success_response(
            message="Team member added successfully.",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)

        serializer = self.get_serializer(
            self.get_object(),
            data=request.data,
            partial=partial,
        )

        if not serializer.is_valid():
            return error_response(
                message="Validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()

        return success_response("Team member updated successfully.", serializer.data)

    def destroy(self, request, *args, **kwargs):
        team_member = self.get_object()
        team_member.soft_delete()

        return success_response(message="Team member removed successfully.")


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsManagerSupervisorLeaderOrReadOnly]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Task.objects.none()

        user = self.request.user

        queryset = Task.objects.filter(deleted_at__isnull=True).select_related(
            "team",
            "team__department",
            "assigned_to",
            "assigned_by",
        )

        if user.is_superuser or user.role == "MANAGER":
            return queryset

        if user.role == "SUPERVISOR":
            return queryset.filter(
                Q(team__department__supervisor=user)
                | Q(team__department__coordinator=user)
            )

        if user.role == "LEADER":
            return queryset.filter(Q(team__leader=user) | Q(team__assistant_leader=user))

        if user.role == "MEMBER":
            return queryset.filter(assigned_to=user)

        return Task.objects.none()

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return success_response("Tasks retrieved successfully.", serializer.data)

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return success_response("Task retrieved successfully.", serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return error_response(
                message="Validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save(assigned_by=request.user)

        return success_response(
            message="Task created successfully.",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        task = self.get_object()

        serializer = self.get_serializer(task, data=request.data, partial=partial)

        if not serializer.is_valid():
            return error_response(
                message="Validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        updated_task = serializer.save()

        if updated_task.status == Task.Status.DONE and updated_task.completed_at is None:
            updated_task.mark_completed()

        return success_response(
            message="Task updated successfully.",
            data=self.get_serializer(updated_task).data,
        )

    def destroy(self, request, *args, **kwargs):
        task = self.get_object()
        task.soft_delete()

        return success_response(message="Task deleted successfully.")


class AchievementViewSet(viewsets.ModelViewSet):
    serializer_class = AchievementSerializer
    permission_classes = [IsManagerSupervisorLeaderOrReadOnly]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Achievement.objects.none()

        user = self.request.user

        queryset = Achievement.objects.filter(deleted_at__isnull=True).select_related(
            "user",
            "team",
            "team__department",
            "created_by",
        )

        if user.is_superuser or user.role == "MANAGER":
            return queryset

        if user.role == "SUPERVISOR":
            return queryset.filter(
                Q(team__department__supervisor=user)
                | Q(team__department__coordinator=user)
            )

        if user.role == "LEADER":
            return queryset.filter(Q(team__leader=user) | Q(team__assistant_leader=user))

        if user.role == "MEMBER":
            return queryset.filter(user=user)

        return Achievement.objects.none()

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return success_response("Achievements retrieved successfully.", serializer.data)

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return success_response("Achievement retrieved successfully.", serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return error_response(
                message="Validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save(created_by=request.user)

        return success_response(
            message="Achievement created successfully.",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)

        serializer = self.get_serializer(
            self.get_object(),
            data=request.data,
            partial=partial,
        )

        if not serializer.is_valid():
            return error_response(
                message="Validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()

        return success_response("Achievement updated successfully.", serializer.data)

    def destroy(self, request, *args, **kwargs):
        achievement = self.get_object()
        achievement.soft_delete()

        return success_response(message="Achievement deleted successfully.")


class MeetingViewSet(viewsets.ModelViewSet):
    serializer_class = MeetingSerializer
    permission_classes = [IsManagerSupervisorLeaderOrReadOnly]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Meeting.objects.none()

        user = self.request.user

        queryset = Meeting.objects.filter(deleted_at__isnull=True).select_related(
            "department",
            "team",
            "team__department",
            "created_by",
        ).prefetch_related("attendees")

        if user.is_superuser or user.role == "MANAGER":
            return queryset

        if user.role == "SUPERVISOR":
            return queryset.filter(
                Q(department__supervisor=user)
                | Q(department__coordinator=user)
                | Q(team__department__supervisor=user)
                | Q(team__department__coordinator=user)
            ).distinct()

        if user.role == "LEADER":
            return queryset.filter(Q(team__leader=user) | Q(team__assistant_leader=user))

        if user.role == "MEMBER":
            return queryset.filter(
                Q(attendees__user=user) | Q(team__memberships__user=user)
            ).distinct()

        return Meeting.objects.none()

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return success_response("Meetings retrieved successfully.", serializer.data)

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return success_response("Meeting retrieved successfully.", serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return error_response(
                message="Validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save(created_by=request.user)

        return success_response(
            message="Meeting created successfully.",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)

        serializer = self.get_serializer(
            self.get_object(),
            data=request.data,
            partial=partial,
        )

        if not serializer.is_valid():
            return error_response(
                message="Validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()

        return success_response("Meeting updated successfully.", serializer.data)

    def destroy(self, request, *args, **kwargs):
        meeting = self.get_object()
        meeting.soft_delete()

        return success_response(message="Meeting deleted successfully.")


class MeetingAttendeeViewSet(viewsets.ModelViewSet):
    serializer_class = MeetingAttendeeSerializer
    permission_classes = [IsManagerSupervisorLeaderOrReadOnly]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return MeetingAttendee.objects.none()

        user = self.request.user

        queryset = MeetingAttendee.objects.select_related(
            "meeting",
            "meeting__department",
            "meeting__team",
            "meeting__team__department",
            "user",
        )

        if user.is_superuser or user.role == "MANAGER":
            return queryset

        if user.role == "SUPERVISOR":
            return queryset.filter(
                Q(meeting__department__supervisor=user)
                | Q(meeting__department__coordinator=user)
                | Q(meeting__team__department__supervisor=user)
                | Q(meeting__team__department__coordinator=user)
            ).distinct()

        if user.role == "LEADER":
            return queryset.filter(
                Q(meeting__team__leader=user) | Q(meeting__team__assistant_leader=user)
            )

        if user.role == "MEMBER":
            return queryset.filter(user=user)

        return MeetingAttendee.objects.none()

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return success_response(
            message="Meeting attendees retrieved successfully.",
            data=serializer.data,
        )

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return success_response("Meeting attendee retrieved successfully.", serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return error_response(
                message="Validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()

        return success_response(
            message="Meeting attendee added successfully.",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)

        serializer = self.get_serializer(
            self.get_object(),
            data=request.data,
            partial=partial,
        )

        if not serializer.is_valid():
            return error_response(
                message="Validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()

        return success_response(
            message="Meeting attendee updated successfully.",
            data=serializer.data,
        )

    def destroy(self, request, *args, **kwargs):
        meeting_attendee = self.get_object()
        meeting_attendee.delete()

        return success_response(message="Meeting attendee removed successfully.")