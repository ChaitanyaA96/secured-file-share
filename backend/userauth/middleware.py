from rest_framework_simplejwt.tokens import AccessToken
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from core.models import User

class CookieJWTMiddleware(MiddlewareMixin):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process the request
        self.process_request(request)
        # Pass the request to the next middleware or view
        response = self.get_response(request)
        return response
    
    def process_request(self, request):
        access_token = request.COOKIES.get("access")
        if not access_token:
            request.user = AnonymousUser()
            return

        try:
            token = AccessToken(access_token)
            user_id = token["user_id"]
        
            request.user = User.objects.get(id=user_id)
        except Exception:
            request.user = AnonymousUser()
