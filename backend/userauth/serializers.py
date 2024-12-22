from rest_framework import serializers

from core.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["id", "email", "password", "first_name", "last_name", "role"]
        extra_kwargs = {"password": {"write_only": True}, "role": {"read_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
