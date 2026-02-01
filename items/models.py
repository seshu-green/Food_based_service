from django.db import models

class Food(models.Model):
    item = models.CharField(max_length=100)
    variant = models.CharField(max_length=100, blank=True)
    method = models.TextField()
    nutrients = models.TextField(blank=True)
    benefits = models.TextField(blank=True)
    hazards = models.TextField(blank=True)

    image_url = models.URLField(blank=True)
    video_url = models.URLField(blank=True)
    source_url = models.URLField(blank=True)

    def save(self, *args, **kwargs):
        if self.variant:
            self.variant = self.variant.lower().strip()  # ✅ DO NOT REMOVE SPACES
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item} - {self.variant}"
