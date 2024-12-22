import pyotp
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from core.models import User


class UserAuthAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        # Pre-generate an MFA secret
        self.secret = pyotp.random_base32()
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="password123",
            mfa_secret=self.secret,
        )
        self.user.is_active = True
        self.user.save()

    def test_register_success(self):
        data = {
            "email": "newuser@example.com",
            "password": "newpassword123",
            "first_name": "New",
            "last_name": "User",
        }
        response = self.client.post(reverse("register"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("Registration successful!", response.data["data"])

    def test_register_existing_email(self):
        data = {"email": "testuser@example.com", "password": "password123"}
        response = self.client.post(reverse("register"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "User with this email is already registered.", response.data["error"]
        )

    def test_verify_email_success(self):
        self.user.is_active = False
        self.user.save()
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        url = reverse("verify-email", kwargs={"uid": uid, "token": token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Email verified successfully", response.data["message"])

    def test_verify_email_already_verified(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        url = reverse("verify-email", kwargs={"uid": uid, "token": token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Email already verified", response.data["message"])

    def test_login_success(self):
        data = {"username": "testuser@example.com", "password": "password123"}
        response = self.client.post(reverse("login"), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("MFA setup required.", response.data["message"])

    def test_login_invalid_credentials(self):
        data = {"username": "testuser@example.com", "password": "wrongpassword"}
        response = self.client.post(reverse("login"), data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("Invalid username or password", response.data["error"])

    def test_logout_success(self):
        # Step 1: Initial login to trigger MFA setup
        login_response = self.client.post(
            reverse("login"),
            {"username": "testuser@example.com", "password": "password123"},
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn("MFA setup required.", login_response.data["message"])

        # Step 2: Complete MFA setup
        otp = pyotp.TOTP(self.secret).now()  # Generate the OTP using PyOTP
        mfa_enable_response = self.client.post(reverse("mfa_enable"), {"otp": otp})
        self.assertEqual(mfa_enable_response.status_code, status.HTTP_200_OK)
        self.assertIn("MFA successfully enabled.", mfa_enable_response.data["message"])

        # Step 3: Perform MFA-authenticated login
        # First step: Login with username and password
        mfa_login_step1_response = self.client.post(
            reverse("login"),
            {"username": "testuser@example.com", "password": "password123"},
        )
        self.assertEqual(mfa_login_step1_response.status_code, status.HTTP_200_OK)
        self.assertIn(
            "Please provide OTP to log in.", mfa_login_step1_response.data["message"]
        )

        # Second step: Provide OTP to complete login
        otp = pyotp.TOTP(self.secret).now()  # Generate a fresh OTP
        mfa_login_step2_response = self.client.post(reverse("otp"), {"otp": otp})
        self.assertEqual(mfa_login_step2_response.status_code, status.HTTP_200_OK)

        # Extract access and refresh token from the final login response
        refresh_token = mfa_login_step2_response.data.get("refresh")
        access_token = mfa_login_step2_response.data.get("access")
        self.assertIsNotNone(refresh_token, "Refresh token should not be None")

        # Step 4: Test logout
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        logout_response = self.client.post(
            reverse("logout"), {"refresh": refresh_token}
        )

        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)
        self.assertIn("Logged out successfully", logout_response.data["message"])

    def test_logout_without_refresh_token(self):
        response = self.client.post(reverse("logout"), {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_enable_mfa_success(self):
        # Simulate login
        login_response = self.client.post(
            reverse("login"),
            {"username": "testuser@example.com", "password": "password123"},
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        # Generate OTP using PyOTP
        otp = pyotp.TOTP(self.secret).now()

        response = self.client.post(reverse("mfa_enable"), {"otp": otp})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("MFA successfully enabled.", response.data["message"])

    def test_enable_mfa_invalid_otp(self):
        # Simulate login
        login_response = self.client.post(
            reverse("login"),
            {"username": "testuser@example.com", "password": "password123"},
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        # Send invalid OTP
        response = self.client.post(reverse("mfa_enable"), {"otp": "invalid-otp"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("Invalid OTP", response.data["error"])

    def test_load_user_data_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("user"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)

    def test_load_user_data_unauthenticated(self):
        response = self.client.get(reverse("user"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_debug_session_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("debug_session"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("user_data", response.data)

    def test_debug_session_unauthenticated(self):
        response = self.client.get(reverse("debug_session"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Anonymous", response.data["user_data"]["role"])
