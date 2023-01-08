import uuid
from pathlib import Path
from functools import partial
from django.db import models
from ..accounts.models import CustomUser


def media_directory_path(filename, forder_name):
    return f'{forder_name}/{str(uuid.uuid4())+Path(filename).suffix}'
    
# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, verbose_name='user')
    user_name = models.CharField(max_length=15, verbose_name="user_name")
    profile_name = models.CharField(max_length=15, verbose_name="profile_name")
    img = models.ImageField(upload_to=partial(media_directory_path, forder_name='profile'))
    
        


class Post(models.Model):
    writer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='writer')
    content = models.CharField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    
class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name='post')
    img = models.ImageField(upload_to='post/%Y/%m/%d')
    img_ratio = models.FloatField()


class PostTag(models.)
    