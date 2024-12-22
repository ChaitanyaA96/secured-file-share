from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import FileResponse, Http404
from core.models import File
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from core.models import File, FileShare
from .serializers import FileSerializer
from django.utils import timezone
import datetime
from django.shortcuts import get_object_or_404
from django.conf import settings
import string
import secrets
from mimetypes import guess_type
from core.utils import send_email 




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

class FileViewView(APIView):
    """
    View a file inline without allowing download.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, file_id, *args, **kwargs):
        try:
            print(f"Attempting to view file with ID: {file_id} for user: {request.user}")
            file = get_object_or_404(File, id=file_id, owner=request.user)
            file_path = file.file.path

            # Decrypt the file content
            decrypted_content = file.decrypt_file()
            mime_type, _ = guess_type(file_path)
            content_type = mime_type or 'application/octet-stream'

            # Stream the file content inline
            response = FileResponse(
                iter([decrypted_content]),
                content_type=content_type,
            )
            response['Content-Disposition'] = f'inline; filename="{file.name}"'
            return response

        except File.DoesNotExist:
            raise Http404("File not found or access denied.")
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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


def generate_shared_link(uri, link, public=False):
    """
    Generate a fully qualified shared link.
    """
    if public:
        return f"{uri.rstrip('/')}/api/files/shared/public/{link}/"
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

        if share_type not in ["view", "download"]:
            return Response(
                {"error": "Invalid share_type. Use 'view' or 'download'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
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
        
        shared_link = generate_shared_link(request.build_absolute_uri('/'), share.shared_link, public=False)
        
        # Send email notification
        email_subject = f"{request.user.first_name} {request.user.last_name} Shared a file with you"
        email_message = f"Shared file details:\n\n"
        email_message += f"File Name: {file_obj.name}\n\n"
        email_message += f"You can {share_type} the file through website \n\n"
        email_message += f"Expires At: {expires_at if expires_at else 'No expiration'}\n"


        recipient_email = shared_with if shared_with else request.user.email
        send_email(
            to=[recipient_email],
            subject=email_subject,
            message=email_message
        )

        return Response({
            "shared_link": shared_link,
            "expires_at": expires_at,
            "public": public,
            "one_time": one_time,
            "passphrase_required": bool(passphrase),
            "passphrase": passphrase  # Optional, send to API response for testing
        }, status=status.HTTP_201_CREATED)


class PublicShareFileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file_id = request.data.get("file_id")
        share_type = request.data.get("share_type")
        expires_in = request.data.get("expires_in")

        file_obj = get_object_or_404(File, id=file_id, owner=request.user)
        expires_at = timezone.now() + datetime.timedelta(hours=int(expires_in)) if expires_in else None 

        if share_type not in ["view", "download"]:
            return Response(
                {"error": "Invalid share_type. Use 'view' or 'download'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        existing_share = FileShare.objects.filter(
            file=file_obj,
            shared_by=request.user,
            public=True,
        ).first()

        if existing_share and existing_share.expires_at > timezone.now():
            return Response({
                "shared_link": generate_shared_link(request.build_absolute_uri('/'), existing_share.shared_link, public=True),
                "expires_at": existing_share.expires_at,
                "passphrase": existing_share.passphrase
            }, status=status.HTTP_201_CREATED)
        
        passphrase = generate_passphrase()

        share = FileShare.objects.create(
            file=file_obj,
            shared_by=request.user,
            shared_with=None,
            share_type=share_type,
            expires_at=expires_at,
            public=True,
            used=False,
            passphrase=passphrase
        )

        shared_link = generate_shared_link(request.build_absolute_uri('/'), share.shared_link, public=True)

        return Response({
            "shared_link": shared_link,
            "expires_at": expires_at,
            "passphrase": passphrase
        }, status=status.HTTP_201_CREATED)


class GetPublicShareDetails(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        file_id = request.query_params.get("file_id")
        user = request.user
        print("file_id" , file_id)
        shareDetails = get_object_or_404(FileShare, file = file_id, public = True, shared_by=user)
        print(shareDetails)
        if shareDetails.expires_at and shareDetails.expires_at < timezone.now():
            return Response({"error": "This link has expired. Please generate a new link."}, status=status.HTTP_400_BAD_REQUEST)
        
        if shareDetails.public:
            return Response({
                "shared_link": generate_shared_link(request.build_absolute_uri('/'), shareDetails.shared_link, public=True),
                "expires_at": shareDetails.expires_at,
                "passphrase": shareDetails.passphrase
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "This link is not public."}, status=status.HTTP_400_BAD_REQUEST)

class AccessSharedFileForAuthenticatedUsers(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, shared_link):
        print(f"Attempting authenticated access for shared file with link: {shared_link}")
        share = get_object_or_404(FileShare, shared_link=shared_link)

        # Check if the link is expired
        if share.is_expired():
            return Response({"error": "This link has expired."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate that the link is not public and is shared with the current user
        if share.public:
            return Response({"error": "This link is public. Use the public API."}, status=status.HTTP_400_BAD_REQUEST)

        if not share.shared_with or request.user.email != share.shared_with:
            return Response({"error": "Access denied."}, status=status.HTTP_403_FORBIDDEN)

        # Handle share_type
        if share.share_type == "view":
            # Stream file content for viewing in the frontend
            file_path = share.file.file.path
            print("file_path", file_path)
            decrypted_content = share.file.decrypt_file()
            mime_type, _ = guess_type(file_path)
            print("mime_type", mime_type)
            content_type = mime_type or "application/octet-stream"

            response = FileResponse(
                iter([decrypted_content]),
                content_type=content_type,
            )
            response["Content-Disposition"] = f'inline; filename="{share.file.name}"'  # Ensure "inline" for viewing
            return response

        elif share.share_type == "download":
            # Allow file download
            file_path = share.file.file.path
            decrypted_content = share.file.decrypt_file()
            mime_type, _ = guess_type(file_path)
            content_type = mime_type or "application/octet-stream"

            response = FileResponse(
                iter([decrypted_content]),
                content_type=content_type,
            )
            response["Content-Disposition"] = f'attachment; filename="{share.file.name}"'  # Allow "attachment" for download
            return response

        return Response({"error": "Invalid share type."}, status=status.HTTP_400_BAD_REQUEST)


class AccessSharedFileForPublicUsers(APIView):
    permission_classes = [AllowAny]

    def get(self, request, shared_link, passphrase):
        print(f"Attempting public access for shared file with link: {shared_link}")
        share = get_object_or_404(FileShare, shared_link=shared_link)

        # Check if the link is expired
        if share.is_expired():
            return Response({"error": "This link has expired."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate that the link is public
        if not share.public:
            return Response({"error": "This link is restricted to authenticated users."}, status=status.HTTP_400_BAD_REQUEST)

        if share.passphrase and share.passphrase != passphrase:
            return Response({"error": "Invalid passphrase."}, status=status.HTTP_403_FORBIDDEN)

        # Handle share_type
        if share.share_type == "view":
            # Stream file content for viewing in the frontend
            file_path = share.file.file.path
            decrypted_content = share.file.decrypt_file()
            mime_type, _ = guess_type(file_path)
            content_type = mime_type or "application/octet-stream"

            response = FileResponse(
                iter([decrypted_content]),
                content_type=content_type,
            )
            response["Content-Disposition"] = f'inline; filename="{share.file.name}"'  # Ensure "inline" for viewing
            return response

        elif share.share_type == "download":
            # Allow file download
            file_path = share.file.file.path
            print("file_path", file_path)
            decrypted_content = share.file.decrypt_file()
            mime_type, _ = guess_type(file_path)
            print("mime_type", mime_type)
            content_type = mime_type or "application/octet-stream"

            response = FileResponse(
                iter([decrypted_content]),
                content_type=content_type,
            )
            response["Content-Disposition"] = f'attachment; filename="{share.file.name}"'  # Allow "attachment" for download
            return response

        return Response({"error": "Invalid share type."}, status=status.HTTP_400_BAD_REQUEST)

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
                    "shared_link": share.shared_link
                })
        return Response(response_data)


class SendEmailView(APIView):
    """
    A view to send an email using the utility function.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Extract email data from the request
        to = request.data.get("to")
        subject = request.data.get("subject")
        message = request.data.get("message")
        from_email = request.user.email

        # Validate inputs
        if not to or not subject or not message:
            return Response(
                {"error": "Missing required fields: 'to', 'subject', or 'message'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(to, list):
            return Response(
                {"error": "'to' field must be a list of recipient email addresses."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Use the utility function to send the email
        try:
            send_email(to=to, subject=subject, message=message, from_email=from_email)
            return Response({"success": "Email sent successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
