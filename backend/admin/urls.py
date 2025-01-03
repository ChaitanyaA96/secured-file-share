from django.urls import path

from .views import (
    FileDetailView,
    FileListView,
    MakeSuperuserView,
    UserDetailView,
    UserListView,
)

urlpatterns = [
    path("users/", UserListView.as_view(), name="user-list"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("files/", FileListView.as_view(), name="file-list"),
    path("files/<str:pk>/", FileDetailView.as_view(), name="file-detail"),
    path(
        "users/<int:pk>/make-superuser/",
        MakeSuperuserView.as_view(),
        name="make-superuser",
    ),
]
