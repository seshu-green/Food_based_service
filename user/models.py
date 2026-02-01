from django.db import models
from django.contrib.auth.models import User

class users(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,null=True,blank=True)  # link to Django user
    name = models.CharField(max_length=128,unique=True)
    dob = models.DateField()

    def __str__(self):
        return self.name
    
class chats(models.Model):
    name = models.CharField(max_length=128, default='***')
    count = models.IntegerField(default=1)
    prompt = models.CharField(max_length=128, default='***')
    bot = models.TextField(default='***')

    image = models.ImageField(
        upload_to="chat_images/",
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['count']

    def __str__(self):
        return f"{self.name} #{self.count}"
