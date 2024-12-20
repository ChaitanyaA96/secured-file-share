from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import Http404
from core.models import File
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from core.models import File, FileShare
from .serializers import FileSerializer
from django.utils import timezone
import datetime
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
import string
import secrets
from mimetypes import guess_type



class FileUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        file_serializer = FileSerializer(data=request.data, context={'request': request})
        if file_serializer.is_valid():
            file_instance = file_serializer.save()
            file_instance.encrypt_file()
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FileDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, file_id, *args, **kwargs):
        try:
            print(f"Attempting to download file with ID: {file_id} for user: {request.user}")
            file = File.objects.get(id=file_id, owner=request.user)
            file_path = file.file.path

            decrypted_content = file.decrypt_file()
            mime_type, _ = guess_type(file_path)
            content_type = mime_type or 'application/octet-stream'

            
            response = FileResponse(
                iter([decrypted_content]),
                content_type=content_type,
            )
            response['Content-Disposition'] = f'attachment; filename="{file.name}"'
            return response
        except File.DoesNotExist:
            raise Http404("File not found or access denied.")

class UserFilesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Retrieve files owned by the logged-in user
        user_files = File.objects.filter(owner=request.user)
        serializer = FileSerializer(user_files, many=True)
        return Response(serializer.data)


# Helper to generate secure passphrase
def generate_passphrase(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))


def generate_shared_link(uri, link):
    """
    Generate a fully qualified shared link.
    """
    return f"{uri.rstrip('/')}/api/files/shared/{link}/"



class ShareFileView(APIView):
    """
    Share a file with another user via email or generate a secure link.
    Includes public, one-time, and restricted sharing.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file_id = request.data.get("file_id")
        share_type = request.data.get("share_type")
        shared_with = request.data.get("shared_with")  # Optional for secure links
        expires_in = request.data.get("expires_in")  # Expiration time in hours
        public = request.data.get("public", False)  # Allow public access
        one_time = request.data.get("one_time", False)  # One-time link flag

        file_obj = get_object_or_404(File, id=file_id, owner=request.user)
        expires_at = timezone.now() + datetime.timedelta(hours=int(expires_in)) if expires_in else None
        passphrase = generate_passphrase() if public else None

        if isinstance(public, str):
            public = public.lower() == "true"
        if isinstance(one_time, str):
            one_time = one_time.lower() == "true"

        share = FileShare.objects.create(
            file=file_obj,
            shared_by=request.user,
            shared_with=shared_with if not public else None,
            share_type=share_type,
            expires_at=expires_at,
            public=public,
            used=one_time,
            passphrase=passphrase
        )
        
        shared_link = generate_shared_link(request.build_absolute_uri('/'), share.shared_link)

        
        # Send email notification
        email_subject = "File Shared with You"
        email_message = f"A file has been shared with you by {request.user.email}.\n\n"
        email_message += f"File Name: {file_obj.name}\n"
        email_message += f"Access Link: {shared_link}\n"
        if passphrase:
            email_message += f"Passphrase: {passphrase}\n"
        email_message += f"Expires At: {expires_at if expires_at else 'No expiration'}\n"

        recipient_email = shared_with if shared_with else request.user.email
        send_mail(
            email_subject,
            email_message,
            from_email=None,  # Uses DEFAULT_FROM_EMAIL from settings
            recipient_list=[recipient_email],
            fail_silently=True,
        )

        return Response({
            "shared_link": shared_link,
            "expires_at": expires_at,
            "public": public,
            "one_time": one_time,
            "passphrase_required": bool(passphrase),
            "passphrase": passphrase  # Optional, send to API response for testing
        }, status=status.HTTP_201_CREATED)


class AccessSharedFileView(APIView):
    """
    Access shared file using a secure link.
    Supports public access, one-time links, and specific user validation.
    """
    permission_classes = [AllowAny]

    def get(self, request, shared_link):
        print(f"Attempting to access shared file with link: {shared_link}")
        share = get_object_or_404(FileShare, shared_link=shared_link)

        # Check if link is expired
        if share.is_expired():
            return Response({"error": "This link has expired."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if link has already been used (for one-time access)
        if share.used:
            return Response({"error": "This link has already been used."}, status=status.HTTP_400_BAD_REQUEST)

        # Check passphrase for public links
        passphrase = request.GET.get("passphrase")
        if share.passphrase and share.passphrase != passphrase:
            return Response({"error": "Invalid passphrase."}, status=status.HTTP_403_FORBIDDEN)

        # Check restricted access for specific user
        if not share.public and share.shared_with and (not request.user.is_authenticated or request.user.email != share.shared_with):
            return Response({"error": "Access denied."}, status=status.HTTP_403_FORBIDDEN)

        # Mark one-time link as used
        if not share.used:
            share.used = True
            share.save()
        
        serializer = FileSerializer(share.file)
        return Response(serializer.data)


class SharedFilesListView(APIView):
    """
    View all files shared with the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        shared_files = FileShare.objects.filter(shared_with=request.user.email, file__isnull=False)
        print(shared_files)
        response_data = []
        for share in shared_files:
            if not share.is_expired():
                print("in expired check",share.shared_link)
                response_data.append({
                    "id": share.id,
                    "file_name": share.file.name,
                    "shared_by": share.shared_by.email,
                    "shared_at": share.created_at,
                    "expires_at": share.expires_at,
                    "share_type": share.share_type,
                    "shared_link": generate_shared_link(request.build_absolute_uri('/'), share.shared_link)
                })
        return Response(response_data)