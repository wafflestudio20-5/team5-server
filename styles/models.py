import uuid
from pathlib import Path
from functools import partial
from django.db import models
from accounts.models import CustomUser


def media_directory_path(filename, forder_name):
    return f'{forder_name}/{str(uuid.uuid4()) + Path(filename).suffix}'


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, primary_key=True, on_delete=models.CASCADE, verbose_name='user')
    user_name = models.CharField(max_length=15, verbose_name="user_name")
    profile_name = models.CharField(max_length=15, verbose_name="profile_name", null=True)
    img = models.ImageField(upload_to=partial(media_directory_path, forder_name='profile'), blank=True, null=True)
    follows = models.ManyToManyField('self', through='Follow', related_name='followed_by', symmetrical=False, blank=True)


class Follow(models.Model):
    from_profile = models.ForeignKey(Profile, related_name='followings', on_delete=models.CASCADE)
    to_profile = models.ForeignKey(Profile, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Post(models.Model):
    writer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='writer')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name='post')
    img = models.ImageField(upload_to='post/%Y/%m/%d')
    img_ratio = models.FloatField()

# class PostTag(models.)
