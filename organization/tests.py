from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from .models import Department, Team

User = get_user_model()


class DepartmentTests(APITestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            email="manager@example.com",
            password="strongpassword123",
            name="Manager User",
            role="MANAGER",
        )
        self.member = User.objects.create_user(
            email="member@example.com",
            password="strongpassword123",
            name="Member User",
            role="MEMBER",
        )

    def test_manager_can_create_department(self):
        self.client.force_authenticate(user=self.manager)

        response = self.client.post(
            reverse("department-list"),
            {
                "name": "Social Engagement Department",
                "description": "Handles content and engagement.",
                "supervisor": self.manager.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data["success"])
        self.assertEqual(Department.objects.count(), 1)


class TeamTests(APITestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            email="manager2@example.com",
            password="strongpassword123",
            name="Manager User",
            role="MANAGER",
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
            email="member2@example.com",
            password="strongpassword123",
            name="Member User",
            role="MEMBER",
        )
        self.department = Department.objects.create(
            name="Project Operation Department",
            supervisor=self.manager,
        )

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
            name="PR Team",
            leader=self.leader,
        )

        self.client.force_authenticate(user=self.member)

        response = self.client.get(reverse("team-list"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["success"])

    def test_soft_delete_team(self):
        team = Team.objects.create(
            department=self.department,
            name="Author Team",
            leader=self.leader,
        )

        self.client.force_authenticate(user=self.manager)

        response = self.client.delete(reverse("team-detail", kwargs={"pk": team.id}))

        team.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(team.deleted_at)