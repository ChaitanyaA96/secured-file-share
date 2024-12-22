from rest_framework import serializers

from core.models import File, User


class UserAdminChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "mfa_enabled",
            "mfa_secret",
            "email_verified",
            "is_active",
            "is_superuser",
            "is_staff",
        ]
        extra_kwargs = {
            "is_superuser": {"read_only": True},
            "is_staff": {"read_only": False},
        }


class MakeSuperuserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "is_superuser"]

    def update(self, instance, validated_data):
        instance.is_superuser = validated_data.get(
            "is_superuser", instance.is_superuser
        )
        instance.save()
        return instance


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ["id", "name", "owner", "file", "uploaded_at", "description"]
