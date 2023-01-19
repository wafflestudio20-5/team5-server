from functools import partial
from django.db import models
from accounts.models import CustomUser
from common.utils import get_media_path


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, primary_key=True, on_delete=models.CASCADE)
    user_name = models.CharField(max_length=15)
    profile_name = models.CharField(max_length=15, unique=True)
    introduction = models.CharField(max_length=100, blank=True, default='')
    image = models.ImageField(upload_to=partial(get_media_path, dir_name='profiles'), null=True)
    follows = models.ManyToManyField('self', through='Follow', related_name='followed_by', symmetrical=False,
                                     blank=True)


class Follow(models.Model):
    from_profile = models.ForeignKey(Profile, related_name='followings', on_delete=models.CASCADE)
    to_profile = models.ForeignKey(Profile, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class Post(models.Model):
    content = models.TextField(max_length=1000)
    created_by = models.ForeignKey(Profile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    image_ratio = models.FloatField()

    class Meta:
        ordering = ['-created_at']


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=partial(get_media_path, dir_name='posts'))


# class PostTag(models.Model):

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.CharField(max_length=100)
    created_by = models.ForeignKey(Profile, on_delete=models.SET_NULL, related_name='comments', null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class Reply(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='replies')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='replies')
    content = models.CharField(max_length=100)
    created_by = models.ForeignKey(Profile, on_delete=models.SET_NULL, related_name='replies', null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

# class Like(models.Model):
