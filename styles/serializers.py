from rest_framework import serializers

from styles.models import Follow, Profile


class NestedProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['user', 'user_name', 'profile_name', 'img']


class FollowerSerializer(serializers.ModelSerializer):
    from_profile = NestedProfileSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ['from_profile', 'created_at']


class FollowingSerializer(serializers.ModelSerializer):
    to_profile = NestedProfileSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ['to_profile', 'created_at']


class ProfileSerializer(serializers.ModelSerializer):
    followers = serializers.SerializerMethodField()
    followings = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['user', 'user_name', 'profile_name', 'img', 'followers', 'followings']
        read_only_fields = ['user', 'followers', 'followings']

    def get_followers(self, obj):
        followers = Follow.objects.filter(to_profile=obj).order_by('-created_at')
        serializer = FollowerSerializer(followers, many=True, read_only=True)
        return serializer.data

    def get_followings(self, obj):
        followings = Follow.objects.filter(from_profile=obj).order_by('-created_at')
        serializer = FollowingSerializer(followings, many=True, read_only=True)
        return serializer.data
