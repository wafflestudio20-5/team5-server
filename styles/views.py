from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from styles.models import Profile, Follow
from styles.serializers import ProfileSerializer, FollowerSerializer, FollowingSerializer
from styles.permissions import IsProfileOwnerOrReadOnly


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsProfileOwnerOrReadOnly]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['current_user'] = self.request.user
        return context


class FollowerListView(generics.ListAPIView):
    serializer_class = FollowerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self, **kwargs):
        return Follow.objects.filter(to_profile__exact=self.kwargs.get('user'))

    def get(self, request, *args, **kwargs):
        followers = self.get_queryset()
        serializer = self.serializer_class(followers, many=True, context={'current_user': self.request.user})
        return Response(serializer.data, status=status.HTTP_200_OK)


class FollowingListView(generics.ListAPIView):
    serializer_class = FollowingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Follow.objects.filter(from_profile__exact=self.kwargs.get('user'))

    def get(self, request, *args, **kwargs):
        followings = self.get_queryset()
        serializer = self.serializer_class(followings, many=True, context={'current_user': self.request.user})
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def follow(request, **kwargs):
    user = request.user
    from_profile = Profile.objects.get(user=user)
    to_profile = get_object_or_404(Profile, pk=kwargs['user'])
    if from_profile == to_profile:
        return HttpResponse('cannot follow or unfollow oneself', status=status.HTTP_400_BAD_REQUEST)

    try:
        follow_instance = Follow.objects.get(from_profile=from_profile, to_profile=to_profile)
        follow_instance.delete()
        return HttpResponse('successfully unfollowed', status=status.HTTP_200_OK)
    except Follow.DoesNotExist:
        Follow.objects.create(from_profile=from_profile, to_profile=to_profile)
        return HttpResponse('successfully followed', status=status.HTTP_200_OK)
