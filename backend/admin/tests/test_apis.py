import pyotp
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from core.models import File, User, UserRole


class AdminTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Create admin and regular users
        self.admin_user = self.create_user(
            email="admin@example.com",
            password="password123",
            role="admin",
            is_superuser=True,
            is_staff=True,
        )
        self.user1 = self.create_user(email="user1@example.com", password="password123")
        self.user2 = self.create_user(email="user2@example.com", password="password123")

        # Authenticate users
        self.tokens_admin = self.authenticate_user(self.admin_user)
        self.tokens_user1 = self.authenticate_user(self.user1)

        # Create a temporary file for testing
        self.temp_file1 = SimpleUploadedFile(
            "testfile1.txt", b"Test file content", content_type="text/plain"
        )
        self.file1 = File.objects.create(
            name="Test File 1", owner=self.user1, file=self.temp_file1
        )

    def create_user(
        self, email, password, role="user", is_superuser=False, is_staff=False
    ):
        """Create a user and complete MFA setup."""
        # Pre-generate an MFA secret
        secret = pyotp.random_base32()
        user = User.objects.create_user(
            email=email,
            password=password,
            mfa_secret=secret,
            is_superuser=is_superuser,
            is_staff=is_staff,
        )
        if role == "admin":
            user.role = UserRole.ADMIN.value
        else:
            user.role = UserRole.USER.value
        user.is_active = True
        user.email_verified = True
        user.save()
        return user

    def authenticate_user(self, user):
        """Authenticate the user and return access and refresh tokens."""
        # Step 1: Login with username and password
        login_response = self.client.post(
            reverse("login"), {"username": user.email, "password": "password123"}
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn("MFA setup required.", login_response.data["message"])

        # Step 2: Complete MFA setup
        otp = pyotp.TOTP(user.mfa_secret).now()  # Generate the OTP using PyOTP
        mfa_enable_response = self.client.post(reverse("mfa_enable"), {"otp": otp})
        self.assertEqual(mfa_enable_response.status_code, status.HTTP_200_OK)
        self.assertIn("MFA successfully enabled.", mfa_enable_response.data["message"])

        # Step 3: Perform MFA-authenticated login
        # Login with username and password
        mfa_login_step1_response = self.client.post(
            reverse("login"), {"username": user.email, "password": "password123"}
        )
        self.assertEqual(mfa_login_step1_response.status_code, status.HTTP_200_OK)
        self.assertIn(
            "Please provide OTP to log in.", mfa_login_step1_response.data["message"]
        )

        # Provide OTP to complete login
        otp = pyotp.TOTP(user.mfa_secret).now()  # Generate a fresh OTP
        mfa_login_step2_response = self.client.post(reverse("otp"), {"otp": otp})
        self.assertEqual(mfa_login_step2_response.status_code, status.HTTP_200_OK)

        # Extract access and refresh tokens
        refresh_token = mfa_login_step2_response.data.get("refresh")
        access_token = mfa_login_step2_response.data.get("access")
        self.assertIsNotNone(refresh_token, "Refresh token should not be None")

        return {
            "access": access_token,
            "refresh": refresh_token,
        }

    # 1. UserListView
    def test_get_user_list(self):
        """Test retrieving the list of users."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.tokens_admin['access']}"
        )
        response = self.client.get(reverse("user-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_user(self):
        """Test creating a new user."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.tokens_admin['access']}"
        )
        data = {
            "email": "testuser@example.com",
            "first_name": "Test",
            "last_name": "User",
            "is_active": True,
            "mfa_enabled": False,
        }
        response = self.client.post(reverse("user-list"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], data["email"])

    # 2. UserDetailView
    def test_get_user_detail(self):
        """Test retrieving details of a specific user."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.tokens_admin['access']}"
        )
        user_id = self.user1.id
        response = self.client.get(reverse("user-detail", args=[user_id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user1.email)

    def test_update_user_detail(self):
        """Test updating details of a specific user."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.tokens_admin['access']}"
        )
        user_id = self.user1.id
        data = {"first_name": "UpdatedName"}
        response = self.client.patch(reverse("user-detail", args=[user_id]), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], data["first_name"])

    def test_delete_user(self):
        """Test deleting a specific user."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.tokens_admin['access']}"
        )
        user_id = self.user1.id
        response = self.client.delete(reverse("user-detail", args=[user_id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # 3. FileListView
    def test_get_file_list(self):
        """Test retrieving the list of files."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.tokens_admin['access']}"
        )
        response = self.client.get(reverse("file-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_file(self):
        """Test creating a new file."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.tokens_admin['access']}"
        )
        temp_file = SimpleUploadedFile(
            "testfile1.txt", b"Test file content", content_type="text/plain"
        )
        data = {
            "name": "Test File",
            "description": "File Description",
            "file": temp_file,
            "owner": self.user1.id,
        }
        response = self.client.post(reverse("file-list"), data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], data["name"])

    # 4. FileDetailView
    def test_get_file_detail(self):
        """Test retrieving details of a specific file."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.tokens_admin['access']}"
        )
        file_id = self.file1.id
        response = self.client.get(reverse("file-detail", args=[file_id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.file1.name)

    def test_update_file_detail(self):
        """Test updating details of a specific file."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.tokens_admin['access']}"
        )
        file_id = self.file1.id
        data = {"description": "Updated Description"}
        response = self.client.patch(reverse("file-detail", args=[file_id]), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["description"], data["description"])

    def test_delete_file(self):
        """Test deleting a specific file."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.tokens_admin['access']}"
        )
        file_id = self.file1.id
        response = self.client.delete(reverse("file-detail", args=[file_id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # 5. MakeSuperuserView
    def test_make_user_superuser(self):
        """Test making a user a superuser."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.tokens_admin['access']}"
        )
        user_id = self.user1.id
        data = {"is_superuser": True}
        response = self.client.patch(reverse("make-superuser", args=[user_id]), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(User.objects.get(id=user_id).is_superuser)

    def test_make_user_superuser_no_permission(self):
        """Test making a user a superuser without required permission."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.tokens_user1['access']}"
        )
        user_id = self.user2.id
        data = {"is_superuser": True}
        response = self.client.patch(reverse("make-superuser", args=[user_id]), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
