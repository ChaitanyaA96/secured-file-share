import json
import uuid

import pyotp
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from core.models import File, FileShare, User
from core.utils import send_email


class FileManagementTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

        # Create two users
        self.user1 = self.create_user(email="user1@example.com", password="password123")
        self.user2 = self.create_user(email="user2@example.com", password="password123")

        # Authenticate and obtain tokens for both users
        self.tokens_user1 = self.authenticate_user(self.user1)
        self.tokens_user2 = self.authenticate_user(self.user2)

        # Create a temporary files for testing
        self.temp_file1 = SimpleUploadedFile(
            "testfile1.txt", b"Test file content", content_type="text/plain"
        )

        self.temp_file2 = SimpleUploadedFile(
            "testfile2.txt", b"Test file content", content_type="text/plain"
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.tokens_user1['access']}"
        )
        upload_response1 = self.client.post(
            reverse("file-upload"),
            {"file": SimpleUploadedFile("testfile.txt", b"Test file content")},
            format="multipart",
        )
        self.assertEqual(upload_response1.status_code, status.HTTP_201_CREATED)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.tokens_user2['access']}"
        )
        upload_response2 = self.client.post(
            reverse("file-upload"),
            {"file": SimpleUploadedFile("testfile.txt", b"Test file content")},
            format="multipart",
        )

        self.assertEqual(upload_response2.status_code, status.HTTP_201_CREATED)
        self.uploaded_file1 = upload_response1.data
        self.uploaded_file2 = upload_response2.data

    def create_user(self, email, password):
        """Create a user and complete MFA setup."""
        # Pre-generate an MFA secret
        secret = pyotp.random_base32()
        user = User.objects.create_user(
            email=email,
            password=password,
            mfa_secret=secret,
        )
        user.is_active = True
        user.email_verified = True
        user.save()
        return user

    def authenticate_user(self, user):
        """Authenticate the user and return access and refresh tokens."""
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
        # First step: Login with username and password
        mfa_login_step1_response = self.client.post(
            reverse("login"), {"username": user.email, "password": "password123"}
        )
        self.assertEqual(mfa_login_step1_response.status_code, status.HTTP_200_OK)
        self.assertIn(
            "Please provide OTP to log in.", mfa_login_step1_response.data["message"]
        )

        # Second step: Provide OTP to complete login
        otp = pyotp.TOTP(user.mfa_secret).now()  # Generate a fresh OTP
        mfa_login_step2_response = self.client.post(reverse("otp"), {"otp": otp})
        self.assertEqual(mfa_login_step2_response.status_code, status.HTTP_200_OK)

        # Extract access and refresh token from the final login response
        refresh_token = mfa_login_step2_response.data.get("refresh")
        access_token = mfa_login_step2_response.data.get("access")
        self.assertIsNotNone(refresh_token, "Refresh token should not be None")

        return {
            "access": access_token,
            "refresh": refresh_token,
        }

    def test_access_shared_file_authenticated_success(self):
        """Test successful access to a shared file by an authenticated user."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.tokens_user1['access']}"
        )
        file = File.objects.create(
            owner=self.user1, file=self.temp_file1, name="testfile1.txt"
        )
        file.encrypt_file()
        share = FileShare.objects.create(
            file=file,
            shared_by=self.user1,
            shared_with=self.user2.email,
            share_type="view",
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.tokens_user2['access']}"
        )
        response = self.client.get(
            reverse(
                "access_shared_file_for_authenticated_users", args=[share.shared_link]
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_access_shared_file_authenticated_forbidden(self):
        """Test access denied for an unauthenticated user trying to access a shared file."""
        file = File.objects.create(
            owner=self.user1, file=self.temp_file1, name="testfile1.txt"
        )
        share = FileShare.objects.create(
            file=file,
            shared_by=self.user1,
            shared_with=self.user2.email,
            share_type="view",
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.tokens_user1['access']}"
        )
        response = self.client.get(
            reverse(
                "access_shared_file_for_authenticated_users", args=[share.shared_link]
            )
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_access_shared_file_public_success(self):
        """Test successful access to a publicly shared file."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.tokens_user1['access']}"
        )
        file = File.objects.create(
            owner=self.user1, file=self.temp_file1, name="testfile1.txt"
        )
        file.encrypt_file()
        share = FileShare.objects.create(
            file=file,
            shared_by=self.user1,
            share_type="view",
            public=True,
            passphrase="securepass",
        )
        response = self.client.get(
            reverse(
                "access_shared_file_for_public_users",
                args=[share.shared_link, "securepass"],
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_access_shared_file_public_invalid_passphrase(self):
        """Test public access denied due to invalid passphrase."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.tokens_user1['access']}"
        )
        file = File.objects.create(
            owner=self.user1, file=self.temp_file1, name="testfile1.txt"
        )
        share = FileShare.objects.create(
            file=file,
            shared_by=self.user1,
            share_type="view",
            public=True,
            passphrase="securepass",
        )
        response = self.client.get(
            reverse(
                "access_shared_file_for_public_users",
                args=[share.shared_link, "wrongpass"],
            )
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_generate_public_link_success(self):
        """Test generating a public link for a file."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.tokens_user1['access']}"
        )
        file = File.objects.create(
            owner=self.user1, file=self.temp_file1, name="testfile1.txt"
        )
        data = {"file_id": file.id, "share_type": "view", "expires_in": 24}
        response = self.client.post(reverse("public_share_file"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("shared_link", response.data)

    def test_generate_public_link_invalid_file(self):
        """Test public link generation fails for an invalid file."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.tokens_user1['access']}"
        )
        data = {"file_id": str(uuid.uuid4()), "share_type": "view", "expires_in": 24}
        response = self.client.post(reverse("public_share_file"), data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_shared_files_list_success(self):
        """Test retrieving a list of files shared with the authenticated user."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.tokens_user1['access']}"
        )
        file = File.objects.create(
            owner=self.user1, file=self.temp_file1, name="testfile1.txt"
        )
        FileShare.objects.create(
            file=file,
            shared_by=self.user1,
            shared_with=self.user2.email,
            share_type="view",
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.tokens_user2['access']}"
        )
        response = self.client.get(reverse("shared_files_list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_send_email_success(self):
        """Test sending an email for file sharing."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.tokens_user1['access']}"
        )
        data = {
            "to": [self.user2.email],
            "subject": "File Sharing Notification",
            "message": "A file has been shared with you.",
        }
        response = self.client.post(
            reverse("send_email"),
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_send_email_missing_fields(self):
        """Test email sending fails with missing required fields."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.tokens_user1['access']}"
        )

        # Missing the 'message' field to trigger the validation error
        data = {
            "to": [self.user2.email],  # Send as a proper list
            "subject": "File Sharing Notification",
        }

        response = self.client.post(
            reverse("send_email"),
            data=json.dumps(data),
            content_type="application/json",
        )

        # Assert that the response status code is 400
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert that the error message mentions the missing fields
        self.assertIn("Missing required fields", response.data["error"])

    def test_file_download_not_found(self):
        """Test downloading a file that does not exist."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.tokens_user1['access']}"
        )
        response = self.client.get(reverse("file-download", args=[str(uuid.uuid4())]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_file_view_unauthorized(self):
        """Test viewing a file not owned by the user."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.tokens_user2['access']}"
        )
        file = File.objects.create(
            owner=self.user1, file=self.temp_file1, name="testfile1.txt"
        )
        response = self.client.get(reverse("file_view", args=[file.id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_user_files(self):
        """Test retrieving a list of files owned by the user."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.tokens_user1['access']}"
        )
        File.objects.create(
            owner=self.user1, file=self.temp_file1, name="testfile1.txt"
        )
        response = self.client.get(reverse("user-files"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_share_file_invalid_type(self):
        """Test sharing a file with an invalid share type."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.tokens_user1['access']}"
        )
        file = File.objects.create(
            owner=self.user1, file=self.temp_file1, name="testfile1.txt"
        )
        data = {"file_id": file.id, "share_type": "invalid"}
        response = self.client.post(reverse("share_file"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_public_share_file_not_found(self):
        """Test sharing a nonexistent file publicly."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.tokens_user1['access']}"
        )
        data = {"file_id": str(uuid.uuid4()), "share_type": "view", "expires_in": 24}
        response = self.client.post(reverse("public_share_file"), data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_shared_files_list_empty(self):
        """Test retrieving an empty list of shared files."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.tokens_user2['access']}"
        )
        response = self.client.get(reverse("shared_files_list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_get_public_share_details_non_public(self):
        """Test retrieving public share details for a non-public file."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.tokens_user1['access']}"
        )
        file = File.objects.create(
            owner=self.user1, file=self.temp_file1, name="testfile1.txt"
        )
        FileShare.objects.create(file=file, shared_by=self.user1, public=False)
        response = self.client.get(
            reverse("get_public_share_details") + f"?file_id={file.id}"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_access_shared_file_invalid_type(self):
        """Test accessing a shared file with an invalid share type."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.tokens_user2['access']}"
        )
        file = File.objects.create(
            owner=self.user1, file=self.temp_file1, name="testfile1.txt"
        )
        share = FileShare.objects.create(
            file=file,
            shared_by=self.user1,
            shared_with=self.user2.email,
            share_type="invalid",
        )
        response = self.client.get(
            reverse(
                "access_shared_file_for_authenticated_users", args=[share.shared_link]
            )
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_access_shared_file_invalid_passphrase(self):
        """Test accessing a publicly shared file with an invalid passphrase."""
        file = File.objects.create(
            owner=self.user1, file=self.temp_file1, name="testfile1.txt"
        )
        share = FileShare.objects.create(
            file=file,
            shared_by=self.user1,
            share_type="view",
            public=True,
            passphrase="correctpass",
        )
        response = self.client.get(
            reverse(
                "access_shared_file_for_public_users",
                args=[share.shared_link, "wrongpass"],
            )
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
