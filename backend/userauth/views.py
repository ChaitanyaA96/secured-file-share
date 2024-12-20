from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer
from django.core.mail import send_mail, EmailMessage
from backend.settings import EMAIL_HOST_USER
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from core.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
import pyotp
from rest_framework_simplejwt.tokens import OutstandingToken, BlacklistedToken
from rest_framework.permissions import IsAuthenticated
import uuid
from django.core.cache import cache as temporary_cache
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from core.models import UserRole
# Create your views here.

class RegisterView(APIView):
    permission_classes = []
    serializer_class = UserSerializer

    def post(self, request):

        email = request.data.get('email')
        if email and User.objects.filter(email=email).exists():
            return Response(
                {"error": "User with this email is already registered."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            password = serializer.validated_data.pop('password')
            if not password:
                return Response({"error": "Password is required"}, status=status.HTTP_400_BAD_REQUEST)  
            user = serializer.save()
            user.set_password(password)
            user.is_active = False
            user.save()
            
            # Generate verification token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Create verification URL
            verification_url = request.build_absolute_uri(
                reverse('verify-email', kwargs={'uid': uid, 'token': token})
            )

            subject = 'Verify your email'
            message = 'Click the link to verify your email: ' + verification_url

            send_mail(
                subject,
                message,
                EMAIL_HOST_USER,
                [user.email],
                fail_silently=True,
            )
            print(serializer.data)
            return Response({"data": "Registration successful! Please check your email for verification. You have 24 hours to verify your account."}, status=status.HTTP_201_CREATED)
        
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
                        {'message': 'Email verified successfully'},
                        status=status.HTTP_200_OK
                    )
                return Response(
                    {'message': 'Email already verified'},
                    status=status.HTTP_200_OK
                )
            
            return Response(
                {'error': 'Invalid or expired verification link'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except (TypeError, ValueError, User.DoesNotExist):
            return Response(
                {'error': 'Invalid verification link'},
                status=status.HTTP_400_BAD_REQUEST
            )

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

            # Blacklist the token
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# class LoginStepOneView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         username = request.data.get("username")
#         password = request.data.get("password")

#         # Authenticate user
#         user = authenticate(username=username, password=password)
#         if not user:
#             return Response({"error": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)

#         if not user.is_active:
#             return Response({"error": "Account is not active"}, status=status.HTTP_403_FORBIDDEN)

#         if not user.mfa_enabled or not user.mfa_secret:
#             secret = pyotp.random_base32()
#             user.mfa_secret = secret
#             user.mfa_enabled = True
#             user.save()

#             otp_url = pyotp.TOTP(secret).provisioning_uri(name=user.email, issuer_name="YourAppName")
#             return Response({
#                 "message": "MFA setup required. Scan the QR code with an authenticator app.",
#                 "otp_url": otp_url
#             }, status=status.HTTP_200_OK)

#         # Success: generate temporary sessiontoken
#         session_token = str(uuid.uuid4())  # Unique token
#         temporary_cache.set(session_token, {"username": username}, timeout=300)

#         # Success: Prompt for OTP in the next step
#         return Response({
#             "message": "Username and password verified. Please provide OTP to continue.",
#             "session_token": session_token
#         }, status=status.HTTP_200_OK)



# class LoginStepTwoView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         session_token = request.data.get("session_token")
#         otp = request.data.get("otp")

#         if not session_token or not otp:
#             return Response({"error": "Please login first using username and password"}, status=status.HTTP_400_BAD_REQUEST)

#         # Retrieve user
#         session_data = temporary_cache.get(session_token)
#         if not session_data:
#             return Response({"error": "Session expired or invalid. Please login again."}, status=status.HTTP_401_UNAUTHORIZED)

#         email = session_data.get("username")
#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             return Response({"error": "Invalid session data. Please login again."}, status=status.HTTP_401_UNAUTHORIZED)
        
#         # Verify OTP dynamically
#         totp = pyotp.TOTP(user.mfa_secret)  # TOTP instance using user's MFA secret
#         if not totp.verify(otp):
#             return Response({"error": "Invalid OTP"}, status=status.HTTP_401_UNAUTHORIZED)

#         # OTP verified; generate JWT tokens
#         refresh = RefreshToken.for_user(user)
#         return Response({
#             "refresh": str(refresh),
#             "access": str(refresh.access_token),
#             "message": "Login successful"
#         }, status=status.HTTP_200_OK)

class LoadUserDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_data = {
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
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
            return Response({"error": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({"error": "Account is not active"}, status=status.HTTP_403_FORBIDDEN)

        # Store user email in the session
        request.session['email'] = user.email

        if not user.mfa_enabled:
            # Generate MFA secret for setup if not already enabled
            if not user.mfa_secret:
                secret = pyotp.random_base32()
                user.mfa_secret = secret
                user.save()
            else:
                secret = user.mfa_secret

            otp_url = pyotp.TOTP(secret).provisioning_uri(name=user.email, issuer_name="YourAppName")
            return Response({
                "message": "MFA setup required. Scan the QR code with an authenticator app.",
                "otp_url": otp_url
            }, status=status.HTTP_200_OK)

        # If MFA is already enabled, prompt for OTP verification
        return Response({
            "message": "Username and password verified. Please provide OTP to log in."
        }, status=status.HTTP_200_OK)


class EnableMFAView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        otp = request.data.get("otp")

        # Check if session exists and retrieve email
        email = request.session.get('email')
        print(email)
        if not email:
            return Response({"error": "Session expired or invalid. Please login again."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            user = User.objects.get(email=email)
            print(user)
        except User.DoesNotExist:
            return Response({"error": "Invalid session data. Please login again."}, status=status.HTTP_401_UNAUTHORIZED)

        # If MFA is already enabled, block this endpoint
        if user.mfa_enabled:
            return Response({"error": "MFA is already enabled for this user."}, status=status.HTTP_400_BAD_REQUEST)

        # Verify OTP using the user's MFA secret
        totp = pyotp.TOTP(user.mfa_secret)
        if not totp.verify(otp):
            return Response({"error": "Invalid OTP"}, status=status.HTTP_401_UNAUTHORIZED)

        # Enable MFA and save
        user.mfa_enabled = True
        user.save()

        return Response({"message": "MFA successfully enabled."}, status=status.HTTP_200_OK)


class LoginStepTwoView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        otp = request.data.get("otp")

        # Ensure OTP is provided
        if not otp:
            return Response({"error": "Please provide OTP to continue."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if session exists and retrieve email
        email = request.session.get('email')
        if not email:
            return Response({"error": "Session expired or invalid. Please login again."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Invalid session data. Please login again."}, status=status.HTTP_401_UNAUTHORIZED)

        # If MFA is not enabled, reject the request
        if not user.mfa_enabled:
            return Response({"error": "MFA is not enabled. Please enable MFA first."}, status=status.HTTP_403_FORBIDDEN)

        # Verify OTP using the user's MFA secret
        totp = pyotp.TOTP(user.mfa_secret)
        if not totp.verify(otp):
            return Response({"error": "Invalid OTP"}, status=status.HTTP_401_UNAUTHORIZED)

        # Generate JWT tokens upon successful login
        refresh = RefreshToken.for_user(user)

        # Clear session data after successful login
        request.session.flush()

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "message": "Login successful"
        }, status=status.HTTP_200_OK)



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
        return Response({
            "user_data": user_data,
            "session_data": session_data,
        })

