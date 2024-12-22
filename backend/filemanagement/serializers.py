from rest_framework import serializers

from core.models import File


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ["id", "owner", "name", "file", "description", "uploaded_at"]
        read_only_fields = ["id", "owner", "uploaded_at"]

    def create(self, validated_data):
        # You can add encryption logic here
        validated_data["owner"] = self.context["request"].user
        return File.objects.create(**validated_data)
