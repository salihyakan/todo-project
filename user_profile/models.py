from django.db import models
from django.contrib.auth.models import User
from autoslug import AutoSlugField


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatar', null=True, blank=True)
    slug = models.SlugField(max_length=200)

