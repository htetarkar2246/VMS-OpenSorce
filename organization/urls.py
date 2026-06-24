from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AchievementViewSet,
    DepartmentViewSet,
    MeetingAttendeeViewSet,
    MeetingViewSet,
    TaskViewSet,
    TeamMemberViewSet,
    TeamViewSet,
)

router = DefaultRouter()
router.register("departments", DepartmentViewSet, basename="department")
router.register("teams", TeamViewSet, basename="team")
router.register("team-members", TeamMemberViewSet, basename="team-member")
router.register("tasks", TaskViewSet, basename="task")
router.register("achievements", AchievementViewSet, basename="achievement")
router.register("meetings", MeetingViewSet, basename="meeting")
router.register("meeting-attendees", MeetingAttendeeViewSet, basename="meeting-attendee")

urlpatterns = [
    path("", include(router.urls)),
]