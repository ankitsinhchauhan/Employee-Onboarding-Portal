from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import User


class AuthFlowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            personal_email="employee@example.com",
            full_name="Test Employee",
            password="SecurePass123!",
            status=User.Status.ACTIVE,
            role=User.Role.EMPLOYEE,
        )

    def test_home_page_loads(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_login_redirects_to_dashboard(self):
        response = self.client.post(
            reverse("login"),
            {"personal_email": "employee@example.com", "password": "SecurePass123!"},
        )
        self.assertRedirects(response, reverse("dashboard"))

    def test_dashboard_requires_authentication(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_authenticated_dashboard_loads(self):
        self.client.login(username="employee@example.com", password="SecurePass123!")
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Employee")
