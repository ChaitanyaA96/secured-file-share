from django.urls import path
from .views import FileUploadView, FileDownloadView, UserFilesView, ShareFileView, AccessSharedFileView, SharedFilesListView

urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('download/<str:file_id>/', FileDownloadView.as_view(), name='file-download'),
    path('my-files/', UserFilesView.as_view(), name='user-files'),
    path('share/', ShareFileView.as_view(), name='share_file'),
    path('shared/<uuid:shared_link>/', AccessSharedFileView.as_view(), name='access_shared_file'),
    path('shared-with-me/', SharedFilesListView.as_view(), name='shared_files_list'),
]