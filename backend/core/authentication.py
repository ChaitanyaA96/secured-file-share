from rest_framework.authentication import BaseAuthentication
from rest_framework_simplejwt.tokens import AccessToken
from core.models import User

class CookieJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        access_token = request.COOKIES.get("access")
        if not access_token:
            return None

        try:
            token = AccessToken(access_token)
            user_id = token["user_id"]
            user = User.objects.get(id=user_id)
            return (user, None)
        except Exception:
            return None
