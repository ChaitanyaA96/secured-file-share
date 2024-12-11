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

# Create your views here.

class RegisterView(APIView):
    permission_classes = []
    serializer_class = UserSerializer

    def post(self, request):
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

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
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


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        otp = request.data.get("otp", None)

        # Authenticate user
        user = authenticate(username=username, password=password)
        if not user:
            return Response({"error": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({"error": "Account is not active"}, status=status.HTTP_403_FORBIDDEN)

        # Check MFA status
        if not user.mfa_enabled:
            # Generate MFA secret and return provisioning URI
            secret = pyotp.random_base32()
            user.mfa_secret = secret
            user.mfa_enabled = True
            user.save()

            otp_url = pyotp.TOTP(secret).provisioning_uri(name=user.email, issuer_name="YourAppName")
            return Response({
                "message": "MFA setup required. Scan the QR code with an authenticator app.",
                "otp_url": otp_url
            }, status=status.HTTP_200_OK)

        # If MFA is active, verify OTP
        if user.mfa_enabled:
            if not otp:
                return Response({"error": "OTP is required for login"}, status=status.HTTP_400_BAD_REQUEST)

            totp = pyotp.TOTP(user.mfa_secret)
            if not totp.verify(otp):
                return Response({"error": "Invalid OTP"}, status=status.HTTP_401_UNAUTHORIZED)

        # Generate JWT tokens after successful OTP verification
        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "message": "Login successful"
        }, status=status.HTTP_200_OK)


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
