from django.db.models import ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from accounts.models import CustomUser
from styles.models import Follow, Profile, Post, Reply, Comment, PostImage


class NestedProfileSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(max_length=None, use_url=True)

    class Meta:
        model = Profile
        fields = ['user_id', 'user_name', 'profile_name', 'image']
        read_only_fields = fields

    def to_representation(self, instance: Profile):
        representation = super().to_representation(instance)
        current_user: CustomUser = self.context['request'].user
        if current_user.is_anonymous:
            return {**representation, 'following': 'login required'}

        if current_user.id == instance.user_id:
            return {**representation, 'following': None}

        following = Follow.objects.filter(from_profile_id=current_user.id, to_profile_id=instance.user_id).exists()
        return {**representation, 'following': following}


class ProfileSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(max_length=None, use_url=True)
    num_posts = serializers.SerializerMethodField()
    num_followers = serializers.SerializerMethodField()
    num_followings = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['user_id', 'user_name', 'profile_name', 'introduction', 'image', 'num_posts', 'num_followers',
                  'num_followings']
        read_only_fields = ['user_id', 'image', 'num_posts', 'num_followers', 'num_followings']

    def get_num_posts(self, obj: Profile):
        return obj.posts.count()

    def get_num_followers(self, obj: Profile):
        return obj.followers.count()

    def get_num_followings(self, obj: Profile):
        return obj.followings.count()

    def to_internal_value(self, data):
        internal_value = super().to_internal_value(data)
        try:
            image = self.context['request'].FILES['image']
            return {**internal_value, 'image': image}
        except KeyError:
            return {**internal_value, 'image': None}

    def to_representation(self, instance: Profile):
        representation = super().to_representation(instance)
        current_user: CustomUser = self.context['request'].user
        if current_user.is_anonymous:
            return {**representation, 'following': 'login required'}

        if current_user.id == instance.user_id:
            return {**representation, 'following': None}

        following = Follow.objects.filter(from_profile_id=current_user.id, to_profile_id=instance.user_id).exists()
        return {**representation, 'following': following}


class FollowerSerializer(serializers.ModelSerializer):
    from_profile = NestedProfileSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ['from_profile', 'created_at']
        read_only_fields = ['from_profile', 'created_at']


class FollowingSerializer(serializers.ModelSerializer):
    to_profile = NestedProfileSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ['to_profile', 'created_at']
        read_only_fields = ['to_profile', 'created_at']


class PostSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    created_by = NestedProfileSerializer(read_only=True)
    num_comments = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'content', 'images', 'image_ratio', 'created_by', 'created_at', 'num_comments']
        read_only_fields = ['id', 'images', 'created_by', 'created_at', 'num_comments']

    def get_images(self, obj: Post):
        return [post_image.image.url for post_image in obj.images.all()]

    def get_num_comments(self, obj: Post):
        return obj.comments.count() + obj.replies.count()

    def create(self, validated_data):
        current_user: CustomUser = self.context['request'].user
        instance = Post.objects.create(**validated_data, created_by_id=current_user.id)
        images = self.context['request'].FILES.getlist('image')
        # if not images:
        #     raise ValidationError('No image has been uploaded')


        for image in images:
            PostImage(post=instance, image=image).save()

        return instance


class ReplySerializer(serializers.ModelSerializer):
    reply_id = serializers.PrimaryKeyRelatedField(read_only=True)
    created_by = NestedProfileSerializer(read_only=True)

    class Meta:
        model = Reply
        fields = ['reply_id', 'content', 'created_by', 'created_at']
        read_only_fields = ['reply_id', 'content', 'created_by', 'created_at']


class CommentSerializer(serializers.ModelSerializer):
    comment_id = serializers.PrimaryKeyRelatedField(read_only=True)
    created_by = NestedProfileSerializer(read_only=True)
    replies = ReplySerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ['comment_id', 'content', 'created_by', 'created_at', 'replies']
        read_only_fields = ['comment_id', 'created_by', 'created_at']