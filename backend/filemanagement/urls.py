from django.urls import path

from .views import (
    AccessSharedFileForAuthenticatedUsers,
    AccessSharedFileForPublicUsers,
    FileDownloadView,
    FileUploadView,
    FileViewView,
    GetPublicShareDetails,
    PublicShareFileView,
    SendEmailView,
    SharedFilesListView,
    ShareFileView,
    UserFilesView,
)

urlpatterns = [
    path("upload/", FileUploadView.as_view(), name="file-upload"),
    path("download/<str:file_id>/", FileDownloadView.as_view(), name="file-download"),
    path("my-files/", UserFilesView.as_view(), name="user-files"),
    path("share/", ShareFileView.as_view(), name="share_file"),
    path("share/public/", PublicShareFileView.as_view(), name="public_share_file"),
    path("shared-with-me/", SharedFilesListView.as_view(), name="shared_files_list"),
    path(
        "shared/public/details/",
        GetPublicShareDetails.as_view(),
        name="get_public_share_details",
    ),
    path(
        "shared/<str:shared_link>/",
        AccessSharedFileForAuthenticatedUsers.as_view(),
        name="access_shared_file_for_authenticated_users",
    ),
    path(
        "shared/public/<str:shared_link>/<str:passphrase>/",
        AccessSharedFileForPublicUsers.as_view(),
        name="access_shared_file_for_public_users",
    ),
    path("view/<str:file_id>/", FileViewView.as_view(), name="file_view"),
    path("send-email/", SendEmailView.as_view(), name="send_email"),
]
