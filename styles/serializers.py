from rest_framework import serializers

from accounts.models import CustomUser
from styles.models import Follow, Profile, Post, Reply, Comment


class NestedProfileSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(max_length=None, use_url=True)

    class Meta:
        model = Profile
        fields = ['user_id', 'user_name', 'profile_name', 'image']

    def to_representation(self, instance: Profile):
        representation = super().to_representation(instance)
        current_user: CustomUser = self.context['current_user']
        if current_user.is_anonymous:
            return {**representation, 'following': 'login required'}

        if current_user.id == instance.user_id:
            return {**representation, 'following': None}

        following = Follow.objects.filter(from_profile_id=current_user.id, to_profile_id=instance.user_id).exists()
        return {**representation, 'following': following}


class ProfileSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(max_length=None, use_url=True)
    num_followers = serializers.SerializerMethodField()
    num_followings = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['user_id', 'user_name', 'profile_name', 'introduction', 'image', 'num_followers', 'num_followings']
        read_only_fields = ['user_id', 'num_followers', 'num_followings']

    def get_num_followers(self, obj: Profile):
        return obj.followers.count()

    def get_num_followings(self, obj: Profile):
        return obj.followings.count()

    def to_representation(self, instance: Profile):
        representation = super().to_representation(instance)
        current_user: CustomUser = self.context['current_user']
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
    created_by = NestedProfileSerializer(read_only=True)
    num_comments = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'content', 'created_by', 'created_at', 'num_comments']
        read_only_fields = ['id', 'created_by', 'created_at', 'num_comments']

    def get_num_comments(self, obj: Post):
        return obj.comments.count() + obj.replies.count()

    def create(self, validated_data):
        current_user: CustomUser = self.context['current_user']
        instance = Post.objects.create(**validated_data, created_by_id=current_user.id)
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
