from django.core.validators import FileExtensionValidator
from django.db import models
from partners.models import Partner


class Story(models.Model):
    name = models.CharField(max_length=100)
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class StoryFile(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(
        upload_to='story_files/',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(['jpg', 'jpeg', 'png', 'mp4'])
        ]
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.story.name

