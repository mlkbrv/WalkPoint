from django.contrib import admin
from .models import Story, StoryFile


class StoryFileInline(admin.TabularInline):
    model = StoryFile
    extra = 1
    fields = ("file", "uploaded_at")
    readonly_fields = ("uploaded_at",)


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "partner", "is_active")
    list_filter = ("is_active", "partner")
    search_fields = ("name", "partner__name")
    list_select_related = ("partner",)
    inlines = [StoryFileInline]


@admin.register(StoryFile)
class StoryFileAdmin(admin.ModelAdmin):
    list_display = ("id", "story", "file", "uploaded_at")
    list_filter = ("uploaded_at", "story")
    search_fields = ("story__name",)
    list_select_related = ("story",)
