from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from .models import Department, Team

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
        )

    def test_manager_can_create_department(self):
        self.client.force_authenticate(user=self.manager)

        response = self.client.post(
            reverse("department-list"),
            {
                "name": "Social Engagement Department",
                "description": "Handles content and engagement.",
                "supervisor": self.supervisor.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data["success"])
        self.assertEqual(Department.objects.count(), 2)

    def test_supervisor_cannot_create_department(self):
        self.client.force_authenticate(user=self.supervisor)

        response = self.client.post(
            reverse("department-list"),
            {
                "name": "Human Resources Department",
                "description": "Handles HR operations.",
                "supervisor": self.supervisor.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_member_cannot_create_department(self):
        self.client.force_authenticate(user=self.member)

        response = self.client.post(
            reverse("department-list"),
            {
                "name": "Financial Department",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_authenticated_user_can_list_departments(self):
        self.client.force_authenticate(user=self.member)

        response = self.client.get(reverse("department-list"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["success"])

    def test_manager_can_create_team(self):
        self.client.force_authenticate(user=self.manager)

        response = self.client.post(
            reverse("team-list"),
            {
                "department": self.department.id,
                "name": "Technical Team",
                "description": "Handles technical development.",
                "leader": self.leader.id,
                "assistant_leader": self.assistant_leader.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data["success"])
        self.assertEqual(Team.objects.count(), 1)

    def test_supervisor_can_create_team(self):
        self.client.force_authenticate(user=self.supervisor)

        response = self.client.post(
            reverse("team-list"),
            {
                "department": self.department.id,
                "name": "PR Team",
                "description": "Handles public relations.",
                "leader": self.leader.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data["success"])
        self.assertEqual(Team.objects.count(), 1)

    def test_leader_cannot_create_team(self):
        self.client.force_authenticate(user=self.leader)

        response = self.client.post(
            reverse("team-list"),
            {
                "department": self.department.id,
                "name": "Author Team",
                "leader": self.leader.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_member_cannot_create_team(self):
        self.client.force_authenticate(user=self.member)

        response = self.client.post(
            reverse("team-list"),
            {
                "department": self.department.id,
                "name": "Finance Team",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_authenticated_user_can_list_teams(self):
        Team.objects.create(
            department=self.department,
            name="Graphic Team",
            leader=self.leader,
        )

        self.client.force_authenticate(user=self.member)

        response = self.client.get(reverse("team-list"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["success"])

    def test_manager_can_soft_delete_department(self):
        self.client.force_authenticate(user=self.manager)

        response = self.client.delete(
            reverse("department-detail", kwargs={"pk": self.department.id})
        )

        self.department.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.department.is_active)
        self.assertIsNotNone(self.department.deleted_at)

    def test_supervisor_can_soft_delete_team(self):
        team = Team.objects.create(
            department=self.department,
            name="Translator Team",
            leader=self.leader,
        )

        self.client.force_authenticate(user=self.supervisor)

        response = self.client.delete(reverse("team-detail", kwargs={"pk": team.id}))

        team.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(team.deleted_at)