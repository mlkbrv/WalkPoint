from rest_framework import serializers
from .models import Story, StoryFile


class StoryFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoryFile
        fields = ["id", "file", "uploaded_at"]


class StorySerializer(serializers.ModelSerializer):
    files = StoryFileSerializer(many=True, read_only=True)

    class Meta:
        model = Story
        fields = ["id", "name", "is_active", "files"]
