from rest_framework import serializers

from styles.models import Follow, Profile


class NestedProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('user', 'user_name', 'profile_name', 'img')


class FollowerSerializer(serializers.ModelSerializer):
    from_profile = NestedProfileSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ('from_profile', 'created_at')


class FollowingSerializer(serializers.ModelSerializer):
    to_profile = NestedProfileSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ('to_profile', 'created_at')


class ProfileSerializer(serializers.ModelSerializer):
    followers = FollowerSerializer(many=True, read_only=True)
    followings = FollowingSerializer(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = ('user', 'user_name', 'profile_name', 'img', 'followers', 'followings')
