from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (  # , ActivateMFAView
    DebugSessionView,
    EnableMFAView,
    LoadUserDataView,
    LoginStepOneView,
    LoginStepTwoView,
    LogoutView,
    RegisterView,
    VerifyEmailView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path(
        "verify-email/<str:uid>/<str:token>/",
        VerifyEmailView.as_view(),
        name="verify-email",
    ),
    path("login/", LoginStepOneView.as_view(), name="login"),
    path("login/otp/", LoginStepTwoView.as_view(), name="otp"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("user/", LoadUserDataView.as_view(), name="user"),
    path("mfa/enable/", EnableMFAView.as_view(), name="mfa_enable"),
    path("debug/session/", DebugSessionView.as_view(), name="debug_session"),
]
