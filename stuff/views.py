from rest_framework.generics import ListAPIView
from .models import Story
from .serializers import StorySerializer


class StoryListView(ListAPIView):
    serializer_class = StorySerializer

    def get_queryset(self):
        return (
            Story.objects.filter(is_active=True)
            .select_related("partner")
            .prefetch_related("files")
        )
