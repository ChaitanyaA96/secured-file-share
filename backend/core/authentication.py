from rest_framework.authentication import BaseAuthentication
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from core.models import User
from rest_framework.exceptions import AuthenticationFailed

class CookieJWTAuthentication(BaseAuthentication):
    """
    Custom authentication class to handle cookie-based JWT authentication
    with automatic access token refresh.
    """

    def authenticate(self, request):
        # Retrieve tokens from cookies
        access_token = request.COOKIES.get("access")
        refresh_token = request.COOKIES.get("refresh")

        if not access_token and not refresh_token:
            return None  # No tokens provided, user remains unauthenticated

        try:
            # Step 1: Validate the access token
            if access_token:
                token = AccessToken(access_token)
                user_id = token["user_id"]
                user = User.objects.get(id=user_id)
                return (user, None)  # Valid access token, no refresh needed

        except Exception:
            # Access token is invalid or expired, proceed to refresh
            pass

        try:
            # Step 2: Attempt to refresh the access token
            if refresh_token:
                refresh = RefreshToken(refresh_token)
                user_id = refresh["user_id"]
                user = User.objects.get(id=user_id)

                # Generate a new access token
                new_access_token = str(refresh.access_token)

                # Attach the new access token to the request
                request.new_access_token = new_access_token

                # Optionally, set the new access token in the response
                # This requires response modification in the view or middleware
                request.refresh_token_refreshed = True

                return (user, None)  # User authenticated with refreshed token

        except Exception as e:
            # If refresh token is invalid or expired, raise an authentication error
            raise AuthenticationFailed("Authentication credentials are invalid or expired.")

        return None
