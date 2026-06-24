from rest_framework import status, viewsets
from rest_framework.response import Response

from .models import Department, Team, TeamMember, Task, Achievement, Meeting, MeetingAttendee
from .permissions import IsManagerOrReadOnly, IsManagerOrSupervisorOrReadOnly, IsManagerSupervisorLeaderOrReadOnly
from .serializers import (
    DepartmentSerializer,
    TeamSerializer,
    TeamMemberSerializer,
    TaskSerializer,
    AchievementSerializer,
    MeetingSerializer,
    MeetingAttendeeSerializer,
)

def envelope(success=True, message="", data=None, errors=None):
    return {
        "success": success,
        "message": message,
        "data": data,
        "errors": errors,
    }


class DepartmentViewSet(viewsets.ModelViewSet):
    serializer_class = DepartmentSerializer
    permission_classes = [IsManagerOrReadOnly]

    def get_queryset(self):
        return Department.objects.filter(deleted_at__isnull=True)

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(envelope(True, "Departments retrieved successfully", serializer.data))

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return Response(envelope(True, "Department retrieved successfully", serializer.data))

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                envelope(True, "Department created successfully", serializer.data),
                status=status.HTTP_201_CREATED,
            )

        return Response(
            envelope(False, "Validation failed", None, serializer.errors),
            status=status.HTTP_400_BAD_REQUEST,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=partial)

        if serializer.is_valid():
            serializer.save()
            return Response(envelope(True, "Department updated successfully", serializer.data))

        return Response(
            envelope(False, "Validation failed", None, serializer.errors),
            status=status.HTTP_400_BAD_REQUEST,
        )

    def destroy(self, request, *args, **kwargs):
        department = self.get_object()
        department.soft_delete()
        return Response(envelope(True, "Department deleted successfully"))


class TeamViewSet(viewsets.ModelViewSet):
    serializer_class = TeamSerializer
    permission_classes = [IsManagerOrSupervisorOrReadOnly]

    def get_queryset(self):
        return Team.objects.filter(deleted_at__isnull=True).select_related(
            "department",
            "leader",
            "assistant_leader",
        )

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(envelope(True, "Teams retrieved successfully", serializer.data))

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return Response(envelope(True, "Team retrieved successfully", serializer.data))

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                envelope(True, "Team created successfully", serializer.data),
                status=status.HTTP_201_CREATED,
            )

        return Response(
            envelope(False, "Validation failed", None, serializer.errors),
            status=status.HTTP_400_BAD_REQUEST,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=partial)

        if serializer.is_valid():
            serializer.save()
            return Response(envelope(True, "Team updated successfully", serializer.data))

        return Response(
            envelope(False, "Validation failed", None, serializer.errors),
            status=status.HTTP_400_BAD_REQUEST,
        )

    def destroy(self, request, *args, **kwargs):
        team = self.get_object()
        team.soft_delete()
        return Response(envelope(True, "Team deleted successfully"))

class TeamMemberViewSet(viewsets.ModelViewSet):
    serializer_class = TeamMemberSerializer
    permission_classes = [IsManagerOrSupervisorOrReadOnly]

    def get_queryset(self):
        return TeamMember.objects.filter(deleted_at__isnull=True).select_related(
            "team",
            "user",
        )

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(envelope(True, "Team members retrieved successfully", serializer.data))

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return Response(envelope(True, "Team member retrieved successfully", serializer.data))

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                envelope(True, "Team member added successfully", serializer.data),
                status=status.HTTP_201_CREATED,
            )

        return Response(
            envelope(False, "Validation failed", None, serializer.errors),
            status=status.HTTP_400_BAD_REQUEST,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        serializer = self.get_serializer(
            self.get_object(),
            data=request.data,
            partial=partial,
        )

        if serializer.is_valid():
            serializer.save()
            return Response(envelope(True, "Team member updated successfully", serializer.data))

        return Response(
            envelope(False, "Validation failed", None, serializer.errors),
            status=status.HTTP_400_BAD_REQUEST,
        )

    def destroy(self, request, *args, **kwargs):
        team_member = self.get_object()
        team_member.soft_delete()
        return Response(envelope(True, "Team member removed successfully"))


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsManagerSupervisorLeaderOrReadOnly]

    def get_queryset(self):
        return Task.objects.filter(deleted_at__isnull=True).select_related(
            "team",
            "assigned_to",
            "assigned_by",
        )

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(envelope(True, "Tasks retrieved successfully", serializer.data))

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return Response(envelope(True, "Task retrieved successfully", serializer.data))

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save(assigned_by=request.user)
            return Response(
                envelope(True, "Task created successfully", serializer.data),
                status=status.HTTP_201_CREATED,
            )

        return Response(
            envelope(False, "Validation failed", None, serializer.errors),
            status=status.HTTP_400_BAD_REQUEST,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        task = self.get_object()

        serializer = self.get_serializer(task, data=request.data, partial=partial)

        if serializer.is_valid():
            updated_task = serializer.save()

            if updated_task.status == Task.Status.DONE and updated_task.completed_at is None:
                updated_task.mark_completed()

            return Response(envelope(True, "Task updated successfully", self.get_serializer(updated_task).data))

        return Response(
            envelope(False, "Validation failed", None, serializer.errors),
            status=status.HTTP_400_BAD_REQUEST,
        )

    def destroy(self, request, *args, **kwargs):
        task = self.get_object()
        task.soft_delete()
        return Response(envelope(True, "Task deleted successfully"))

class AchievementViewSet(viewsets.ModelViewSet):
    serializer_class = AchievementSerializer
    permission_classes = [IsManagerSupervisorLeaderOrReadOnly]

    def get_queryset(self):
        return Achievement.objects.filter(deleted_at__isnull=True).select_related(
            "user",
            "team",
            "created_by",
        )

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(envelope(True, "Achievements retrieved successfully", serializer.data))

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return Response(envelope(True, "Achievement retrieved successfully", serializer.data))

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(
                envelope(True, "Achievement created successfully", serializer.data),
                status=status.HTTP_201_CREATED,
            )

        return Response(
            envelope(False, "Validation failed", None, serializer.errors),
            status=status.HTTP_400_BAD_REQUEST,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=partial)

        if serializer.is_valid():
            serializer.save()
            return Response(envelope(True, "Achievement updated successfully", serializer.data))

        return Response(
            envelope(False, "Validation failed", None, serializer.errors),
            status=status.HTTP_400_BAD_REQUEST,
        )

    def destroy(self, request, *args, **kwargs):
        achievement = self.get_object()
        achievement.soft_delete()
        return Response(envelope(True, "Achievement deleted successfully"))


class MeetingViewSet(viewsets.ModelViewSet):
    serializer_class = MeetingSerializer
    permission_classes = [IsManagerSupervisorLeaderOrReadOnly]

    def get_queryset(self):
        return Meeting.objects.filter(deleted_at__isnull=True).select_related(
            "department",
            "team",
            "created_by",
        ).prefetch_related("attendees")

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(envelope(True, "Meetings retrieved successfully", serializer.data))

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return Response(envelope(True, "Meeting retrieved successfully", serializer.data))

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(
                envelope(True, "Meeting created successfully", serializer.data),
                status=status.HTTP_201_CREATED,
            )

        return Response(
            envelope(False, "Validation failed", None, serializer.errors),
            status=status.HTTP_400_BAD_REQUEST,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=partial)

        if serializer.is_valid():
            serializer.save()
            return Response(envelope(True, "Meeting updated successfully", serializer.data))

        return Response(
            envelope(False, "Validation failed", None, serializer.errors),
            status=status.HTTP_400_BAD_REQUEST,
        )

    def destroy(self, request, *args, **kwargs):
        meeting = self.get_object()
        meeting.soft_delete()
        return Response(envelope(True, "Meeting deleted successfully"))


class MeetingAttendeeViewSet(viewsets.ModelViewSet):
    serializer_class = MeetingAttendeeSerializer
    permission_classes = [IsManagerSupervisorLeaderOrReadOnly]

    def get_queryset(self):
        return MeetingAttendee.objects.select_related("meeting", "user")

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(envelope(True, "Meeting attendees retrieved successfully", serializer.data))

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return Response(envelope(True, "Meeting attendee retrieved successfully", serializer.data))

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                envelope(True, "Meeting attendee added successfully", serializer.data),
                status=status.HTTP_201_CREATED,
            )

        return Response(
            envelope(False, "Validation failed", None, serializer.errors),
            status=status.HTTP_400_BAD_REQUEST,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=partial)

        if serializer.is_valid():
            serializer.save()
            return Response(envelope(True, "Meeting attendee updated successfully", serializer.data))

        return Response(
            envelope(False, "Validation failed", None, serializer.errors),
            status=status.HTTP_400_BAD_REQUEST,
        )