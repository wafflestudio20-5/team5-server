from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from accounts.models import CustomUser
from styles.models import Profile, Follow, Post, Comment, Reply
from styles.serializers import ProfileSerializer, FollowerSerializer, FollowingSerializer, PostSerializer, \
    CommentSerializer
from styles.permissions import IsProfileOwnerOrReadOnly, IsPostWriterOrReadOnly


class ProfileRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsProfileOwnerOrReadOnly]
    lookup_field = 'user_id'

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['current_user'] = self.request.user
        return context


class FollowerListAPIView(generics.ListAPIView):
    serializer_class = FollowerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Follow.objects.filter(to_profile__exact=self.kwargs.get('user_id'))

    def get(self, request, *args, **kwargs):
        followers = self.get_queryset()
        serializer = self.serializer_class(followers, many=True, context={'current_user': self.request.user})
        return JsonResponse(serializer.data, status=status.HTTP_200_OK)


class FollowingListAPIView(generics.ListAPIView):
    serializer_class = FollowingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Follow.objects.filter(from_profile__exact=self.kwargs.get('user_id'))

    def get(self, request, *args, **kwargs):
        followings = self.get_queryset()
        serializer = self.serializer_class(followings, many=True, context={'current_user': self.request.user})
        return JsonResponse(serializer.data, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def follow(request, **kwargs):
    from_profile = Profile.objects.get(user=request.user)
    to_profile = get_object_or_404(Profile, pk=kwargs['user_id'])
    if from_profile == to_profile:
        return JsonResponse({'message': 'cannot follow or unfollow oneself'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        follow_instance = Follow.objects.get(from_profile=from_profile, to_profile=to_profile)
        follow_instance.delete()
        return JsonResponse({'message': 'successfully unfollowed'}, status=status.HTTP_200_OK)
    except Follow.DoesNotExist:
        Follow.objects.create(from_profile=from_profile, to_profile=to_profile)
        return JsonResponse({'message': 'successfully followed'}, status=status.HTTP_200_OK)


class PostListCreateAPIView(generics.ListCreateAPIView):
    queryset = Post.objects.select_related('created_by').all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['current_user'] = self.request.user
        return context

    def get(self, request, *args, **kwargs):
        feed_type = self.request.query_params.get('type', None)
        if feed_type is None:
            return JsonResponse({'message': (
                'query parameter "type" required\n'
                'the type should be one of: "popular", "latest", "following", and "default"\n'
            )}, status=status.HTTP_400_BAD_REQUEST)

        if feed_type == 'popular':
            return JsonResponse({'message': 'not implemented yet'}, status=status.HTTP_400_BAD_REQUEST)

        if feed_type == 'latest':
            posts = self.get_queryset()
            serializer = self.serializer_class(posts, many=True)
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)

        if feed_type == 'following':
            user: CustomUser = request.user
            if user.is_anonymous:
                return JsonResponse({'message': 'login required'}, status=status.HTTP_401_UNAUTHORIZED)

            current_profile = Profile.objects.get(user=user)
            posts = self.queryset.filter(
                created_by__in=[follow_instance.to_profile for follow_instance in current_profile.followings.all()]
            ).order_by('-created_at')
            serializer = self.serializer_class(posts, many=True)
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)

        if feed_type == 'default':
            user_id = self.request.query_params.get('user_id')
            if user_id is None:
                return JsonResponse({'message': 'query parameter "user_id" required for the default type'},
                                    status=status.HTTP_400_BAD_REQUEST)

            writer = get_object_or_404(Profile, pk=user_id)
            posts = self.queryset.filter(created_by=writer)
            serializer = self.serializer_class(posts, many=True)
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)

        return JsonResponse({'message': (
            'invalid query parameter "type"\n'
            'the type should be one of: "popular", "latest", "following", and "default"\n'
        )}, status=status.HTTP_400_BAD_REQUEST)


class PostRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.select_related('created_by').all()
    serializer_class = PostSerializer
    permission_classes = [IsPostWriterOrReadOnly]
    lookup_field = 'post_id'


class CommentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        return Comment.objects.select_related('post', 'created_by').filter(post_id__exact=self.kwargs.get('post_id'))

# class ReplyRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
