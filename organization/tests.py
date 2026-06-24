from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from .models import (
    Achievement,
    Department,
    Meeting,
    MeetingAttendee,
    Task,
    Team,
    TeamMember,
)

User = get_user_model()


class OrganizationTests(APITestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            email="manager@example.com",
            password="strongpassword123",
            name="Manager User",
            role="MANAGER",
        )
        self.supervisor = User.objects.create_user(
            email="supervisor@example.com",
            password="strongpassword123",
            name="Supervisor User",
            role="SUPERVISOR",
        )
        self.coordinator = User.objects.create_user(
            email="coordinator@example.com",
            password="strongpassword123",
            name="Coordinator User",
            role="SUPERVISOR",
        )
        self.leader = User.objects.create_user(
            email="leader@example.com",
            password="strongpassword123",
            name="Leader User",
            role="LEADER",
        )
        self.assistant_leader = User.objects.create_user(
            email="assistant@example.com",
            password="strongpassword123",
            name="Assistant Leader User",
            role="LEADER",
        )
        self.member = User.objects.create_user(
            email="member@example.com",
            password="strongpassword123",
            name="Member User",
            role="MEMBER",
        )

        self.department = Department.objects.create(
            name="Project Operation Department",
            supervisor=self.supervisor,
            coordinator=self.coordinator,
        )

        self.team = Team.objects.create(
            department=self.department,
            name="Technical Team",
            leader=self.leader,
            assistant_leader=self.assistant_leader,
        )

    def test_manager_can_create_department(self):
        self.client.force_authenticate(user=self.manager)

        response = self.client.post(
            reverse("department-list"),
            {
                "name": "Social Engagement Department",
                "description": "Handles content and engagement.",
                "supervisor": self.supervisor.id,
                "coordinator": self.coordinator.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data["success"])

    def test_supervisor_cannot_create_department(self):
        self.client.force_authenticate(user=self.supervisor)

        response = self.client.post(
            reverse("department-list"),
            {"name": "Human Resources Department"},
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_manager_can_create_team(self):
        self.client.force_authenticate(user=self.manager)

        response = self.client.post(
            reverse("team-list"),
            {
                "department": self.department.id,
                "name": "PR Team",
                "description": "Handles PR.",
                "leader": self.leader.id,
                "assistant_leader": self.assistant_leader.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data["success"])

    def test_supervisor_can_create_team(self):
        self.client.force_authenticate(user=self.supervisor)

        response = self.client.post(
            reverse("team-list"),
            {
                "department": self.department.id,
                "name": "Author Team",
                "leader": self.leader.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)

    def test_leader_cannot_create_team(self):
        self.client.force_authenticate(user=self.leader)

        response = self.client.post(
            reverse("team-list"),
            {
                "department": self.department.id,
                "name": "Finance Team",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_supervisor_can_add_team_member(self):
        self.client.force_authenticate(user=self.supervisor)

        response = self.client.post(
            reverse("team-member-list"),
            {
                "team": self.team.id,
                "user": self.member.id,
                "team_role": "MEMBER",
                "member_type": "MAIN",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(TeamMember.objects.count(), 1)

    def test_leader_cannot_add_team_member(self):
        self.client.force_authenticate(user=self.leader)

        response = self.client.post(
            reverse("team-member-list"),
            {
                "team": self.team.id,
                "user": self.member.id,
                "team_role": "MEMBER",
                "member_type": "MAIN",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_leader_can_create_task(self):
        self.client.force_authenticate(user=self.leader)

        response = self.client.post(
            reverse("task-list"),
            {
                "team": self.team.id,
                "assigned_to": self.member.id,
                "title": "Build API endpoint",
                "description": "Create task API endpoint.",
                "status": "TODO",
                "priority": "HIGH",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Task.objects.count(), 1)

    def test_member_cannot_create_task(self):
        self.client.force_authenticate(user=self.member)

        response = self.client.post(
            reverse("task-list"),
            {
                "team": self.team.id,
                "assigned_to": self.member.id,
                "title": "Unauthorized task",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_leader_can_create_achievement(self):
        self.client.force_authenticate(user=self.leader)

        response = self.client.post(
            reverse("achievement-list"),
            {
                "user": self.member.id,
                "team": self.team.id,
                "title": "Completed API Module",
                "description": "Finished authentication API.",
                "achievement_date": "2026-06-24",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Achievement.objects.count(), 1)

    def test_leader_can_create_meeting(self):
        self.client.force_authenticate(user=self.leader)

        start_time = timezone.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)

        response = self.client.post(
            reverse("meeting-list"),
            {
                "title": "Technical Team Meeting",
                "description": "Weekly technical sync.",
                "meeting_type": "TEAM",
                "team": self.team.id,
                "start_datetime": start_time.isoformat(),
                "end_datetime": end_time.isoformat(),
                "location": "Google Meet",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Meeting.objects.count(), 1)

    def test_leader_can_add_meeting_attendee(self):
        meeting = Meeting.objects.create(
            title="Team Meeting",
            meeting_type="TEAM",
            team=self.team,
            created_by=self.leader,
            start_datetime=timezone.now() + timedelta(days=1),
            end_datetime=timezone.now() + timedelta(days=1, hours=1),
        )

        self.client.force_authenticate(user=self.leader)

        response = self.client.post(
            reverse("meeting-attendee-list"),
            {
                "meeting": meeting.id,
                "user": self.member.id,
                "status": "INVITED",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(MeetingAttendee.objects.count(), 1)