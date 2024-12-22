from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import TestCase

from core.admin import UserAdmin


class UserAdminTestCase(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.superuser = self.user_model.objects.create_superuser(
            email="admin@example.com", password="adminpassword"
        )
        self.admin = UserAdmin(self.user_model, AdminSite())

    def test_user_admin_list_display(self):
        self.assertIn("email", self.admin.list_display)
        self.assertIn("is_staff", self.admin.list_display)

    def test_user_admin_search_fields(self):
        self.assertIn("email", self.admin.search_fields)
