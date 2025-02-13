import pyotp
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken

from backend.django_settings import EMAIL_HOST_USER
from core.models import User, UserRole

from .serializers import UserSerializer

# Create your views here.


class RegisterView(APIView):
    permission_classes = []
    serializer_class = UserSerializer

    def post(self, request):

        email = request.data.get("email")
        if email and User.objects.filter(email=email).exists():
            return Response(
                {"error": "User with this email is already registered."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            password = serializer.validated_data.pop("password")
            if not password:
                return Response(
                    {"error": "Password is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user = serializer.save()
            user.set_password(password)
            user.is_active = False
            user.save()

            # Generate verification token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            # Create verification URL
            verification_url = request.build_absolute_uri(
                reverse("verify-email", kwargs={"uid": uid, "token": token})
            )

            subject = "Verify your email"
            message = "Click the link to verify your email: " + verification_url

            send_mail(
                subject,
                message,
                EMAIL_HOST_USER,
                [user.email],
                fail_silently=True,
            )
            return Response(
                {
                    "data": "Registration successful! Please check your email for verification. You have 24 hours to verify your account."
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    permission_classes = []

    def get(self, request, uid, token):
        try:
            user_id = urlsafe_base64_decode(uid).decode()
            user = User.objects.get(pk=user_id)

            if default_token_generator.check_token(user, token):
                if not user.is_active:
                    user.is_active = True
                    user.email_verified = True
                    user.role = UserRole.USER.value
                    user.save()
                    return Response(
                        {"message": "Email verified successfully"},
                        status=status.HTTP_200_OK,
                    )
                return Response(
                    {"message": "Email already verified"}, status=status.HTTP_200_OK
                )

            return Response(
                {"error": "Invalid or expired verification link"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except (TypeError, ValueError, User.DoesNotExist):
            return Response(
                {"error": "Invalid verification link"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.COOKIES.get("refresh")
            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            
            if request.user.is_anonymous:
                return Response(
                    {"message": "No user is authenticated."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # Blacklist the token
            token = RefreshToken(refresh_token)
            token.blacklist()

            response = Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
            response.delete_cookie("access")
            response.delete_cookie("refresh")

            return response
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LoadUserDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Unauthenticated"}, status=status.HTTP_401_UNAUTHORIZED)
        user = request.user
        user_data = {
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
        }
        return Response(user_data, status=status.HTTP_200_OK)


class LoginStepOneView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        # Authenticate user
        user = authenticate(username=username, password=password)
        if not user:
            return Response(
                {"error": "Invalid username or password"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {"error": "Account is not active"}, status=status.HTTP_403_FORBIDDEN
            )

        # Store user email in the session
        request.session["email"] = user.email

        if not user.mfa_enabled:
            # Generate MFA secret for setup if not already enabled
            if not user.mfa_secret:
                secret = pyotp.random_base32()
                user.mfa_secret = secret
                user.save()
            else:
                secret = user.mfa_secret

            otp_url = pyotp.TOTP(secret).provisioning_uri(
                name=user.email, issuer_name="YourAppName"
            )
            return Response(
                {
                    "message": "MFA setup required. Scan the QR code with an authenticator app.",
                    "otp_url": otp_url,
                },
                status=status.HTTP_200_OK,
            )

        # If MFA is already enabled, prompt for OTP verification
        return Response(
            {
                "message": "Username and password verified. Please provide OTP to log in."
            },
            status=status.HTTP_200_OK,
        )


class EnableMFAView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        otp = request.data.get("otp")

        # Check if session exists and retrieve email
        email = request.session.get("email")
        if not email:
            return Response(
                {"error": "Session expired or invalid. Please login again."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid session data. Please login again."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # If MFA is already enabled, block this endpoint
        if user.mfa_enabled:
            return Response(
                {"error": "MFA is already enabled for this user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Verify OTP using the user's MFA secret
        totp = pyotp.TOTP(user.mfa_secret)
        if not totp.verify(otp):
            return Response(
                {"error": "Invalid OTP"}, status=status.HTTP_401_UNAUTHORIZED
            )

        # Enable MFA and save
        user.mfa_enabled = True
        user.save()

        return Response(
            {"message": "MFA successfully enabled."}, status=status.HTTP_200_OK
        )


class LoginStepTwoView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        otp = request.data.get("otp")

        # Ensure OTP is provided
        if not otp:
            return Response(
                {"error": "Please provide OTP to continue."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if session exists and retrieve email
        email = request.session.get("email")

        if not email:
            return Response(
                {"error": "Session expired or invalid. Please login again."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid session data. Please login again."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # If MFA is not enabled, reject the request
        if not user.mfa_enabled:
            return Response(
                {"error": "MFA is not enabled. Please enable MFA first."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Verify OTP using the user's MFA secret
        totp = pyotp.TOTP(user.mfa_secret)
        if not totp.verify(otp):
            return Response(
                {"error": "Invalid OTP"}, status=status.HTTP_401_UNAUTHORIZED
            )

        # Generate JWT tokens upon successful login
        refresh = RefreshToken.for_user(user)

        # Clear session data after successful login
        request.session.flush()

        response = Response({"message": "Login successful", "role": user.role}, status=status.HTTP_200_OK,)

        response.set_cookie(
            key="access",
            value=str(refresh.access_token),
            httponly=True,
            secure=True,
            samesite="Lax",
        )
        response.set_cookie(
            key="refresh",
            value=str(refresh),
            httponly=True,
            secure=True,
            samesite="Lax",
        )

        return response


class DebugSessionView(APIView):
    permission_classes = []  # Allow any access

    def get(self, request):
        user_data = {
            "user": str(request.user),
            "is_authenticated": request.user.is_authenticated,
            # Safely access user attributes if authenticated
            "role": getattr(request.user, "role", "Anonymous"),
        }
        session_data = dict(request.session.items())
        return Response(
            {
                "user_data": user_data,
                "session_data": session_data,
            }
        )

class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        # Retrieve refresh token from cookies
        refresh_token = request.COOKIES.get("refresh")
        if not refresh_token:
            return Response(
                {"error": "Refresh token is missing or invalid."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Update the request data to include the refresh token
        request.data["refresh"] = refresh_token
        try:
            # Use the parent class logic to refresh tokens
            response = super().post(request, *args, **kwargs)
            access_token = response.data.get("access")

            # Create a new response with updated access token in cookies
            new_response = Response({"message": "Token refreshed successfully"})
            new_response.set_cookie(
                key="access",
                value=access_token,
                httponly=True,
                secure=True,
                samesite="Lax",
            )
            return new_response
        except InvalidToken:
            return Response(
                {"error": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED
            )
