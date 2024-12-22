from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import File, User
from core.permissions import IsAdmin, IsSuperuser

from .serializers import (
    FileSerializer,
    MakeSuperuserSerializer,
    UserAdminChangeSerializer,
)


class UserListView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserAdminChangeSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserAdminChangeSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


class FileListView(generics.ListCreateAPIView):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


class FileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


class MakeSuperuserView(APIView):
    permission_classes = [IsAuthenticated, IsSuperuser]

    def patch(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=kwargs["pk"])
        serializer = MakeSuperuserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"status": "success", "message": "User is now a superuser"},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
