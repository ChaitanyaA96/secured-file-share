from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from core.models import User
import logging

logger = logging.getLogger(__name__)

class CookieJWTMiddleware(MiddlewareMixin):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process the request
        self.process_request(request)
        # Pass the request to the next middleware or view
        
        response = self.get_response(request)

        if hasattr(request, "new_access_token"):
            response.set_cookie(
                key="access",
                value=request.new_access_token,
                httponly=True,
                secure=True,
                samesite="Lax",
            )
        return response
    
    def process_request(self, request):
        access_token = request.COOKIES.get("access")
        refresh_token = request.COOKIES.get("refresh")

        request.user = AnonymousUser()

        if access_token:
            try:
                token = AccessToken(access_token)
                user_id = token["user_id"]
                request.user = User.objects.get(id=user_id)
                return  # Valid access token, no further action needed
            except Exception as e:
                pass

        if refresh_token:
            try:
                refresh = RefreshToken(refresh_token)
                user_id = refresh["user_id"]
                user = User.objects.get(id=user_id)

                # Set the authenticated user
                request.user = user

                # Generate a new access token
                new_access_token = refresh.access_token
                # Attach the new access token as a cookie
                request.new_access_token = str(new_access_token)

            except Exception as e:
                request.user = AnonymousUser()
