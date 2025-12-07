from django.urls import path
from .views import StoryListView

urlpatterns = [
    path("stories/", StoryListView.as_view(), name="stories"),
]
