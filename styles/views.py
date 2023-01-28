from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser

from accounts.models import CustomUser
from styles.models import Profile, Follow, Post, Comment, Reply, Like
from styles.paginations import CommonCursorPagination
from styles.permissions import IsProfileOwnerOrReadOnly, IsWriterOrReadOnly
from styles.serializers import ProfileSerializer, FollowerSerializer, FollowingSerializer, PostSerializer, \
    CommentListSerializer, CommentDetailSerializer, ReplySerializer, LikeListSerializer
from styles.exceptions import InvalidObjectTypeException


class ProfileListAPIView(generics.ListAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAdminUser]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class ProfileRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsProfileOwnerOrReadOnly]
    lookup_field = 'user_id'

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class FollowerListAPIView(generics.ListAPIView):
    serializer_class = FollowerSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CommonCursorPagination

    def get_queryset(self):
        return Follow.objects.filter(to_profile__exact=self.kwargs.get('user_id'))

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class FollowingListAPIView(generics.ListAPIView):
    serializer_class = FollowingSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CommonCursorPagination

    def get_queryset(self):
        return Follow.objects.filter(from_profile__exact=self.kwargs.get('user_id'))

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


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
    queryset = Post.objects.select_related('created_by').prefetch_related('images').all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = CommonCursorPagination

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)

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
            queryset = self.get_queryset()
            page = self.paginate_queryset(queryset)
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        if feed_type == 'following':
            user: CustomUser = request.user
            if user.is_anonymous:
                return JsonResponse({'message': 'login required'}, status=status.HTTP_401_UNAUTHORIZED)

            current_profile = Profile.objects.get(user=user)
            queryset = self.get_queryset().filter(
                created_by__in=[follow_instance.to_profile for follow_instance in current_profile.followings.all()])
            page = self.paginate_queryset(queryset)
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        if feed_type == 'default':
            user_id = self.request.query_params.get('user_id')
            if user_id is None:
                return JsonResponse({'message': 'query parameter "user_id" required for the default type'},
                                    status=status.HTTP_400_BAD_REQUEST)

            writer = get_object_or_404(Profile, pk=user_id)
            queryset = self.get_queryset().filter(created_by=writer)
            page = self.paginate_queryset(queryset)
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        return JsonResponse({'message': (
            'invalid query parameter "type"\n'
            'the type should be one of: "popular", "latest", "following", and "default"\n'
        )}, status=status.HTTP_400_BAD_REQUEST)


class PostRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.select_related('created_by').prefetch_related('images').all()
    serializer_class = PostSerializer
    permission_classes = [IsWriterOrReadOnly]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class CommentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CommentListSerializer
    permission_classes = [IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        get_object_or_404(Post, pk=self.kwargs.get('pk'))
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Comment.objects.select_related('created_by').prefetch_related('replies').filter(
            post_id__exact=self.kwargs.get('pk'))

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        context['post_id'] = self.kwargs.get('pk')
        return context


class CommentRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.select_related('created_by').prefetch_related('replies').all()
    serializer_class = CommentDetailSerializer
    permission_classes = [IsAuthenticated & IsWriterOrReadOnly]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class ReplyListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ReplySerializer
    permission_classes = [IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        get_object_or_404(Comment, pk=self.kwargs.get('pk'))
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Reply.objects.select_related('created_by').filter(
            comment_id__exact=self.kwargs.get('pk'))

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        context['comment_id'] = self.kwargs.get('pk')
        return context


class ReplyRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reply.objects.select_related('created_by').all()
    serializer_class = ReplySerializer
    permission_classes = [IsAuthenticated & IsWriterOrReadOnly]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def like(request, **kwargs):
    if kwargs['object_type'] == 'posts':
        obj = get_object_or_404(Post, id=kwargs['object_id'])
    elif kwargs['object_type'] == 'comments':
        obj = get_object_or_404(Comment, id=kwargs['object_id'])
    elif kwargs['object_type'] == 'replies':
        obj = get_object_or_404(Reply, id=kwargs['object_id'])
    else:
        raise InvalidObjectTypeException()

    profile = Profile.objects.get(user=request.user)
    try:
        like_instance = Like.objects.get(profile=profile, content_type=ContentType.objects.get_for_model(obj),
                                         object_id=obj.id)
        like_instance.delete()
        return JsonResponse({'message': 'unliked successfully'}, status=status.HTTP_200_OK)

    except Like.DoesNotExist:
        Like.objects.create(profile=profile, content_type=ContentType.objects.get_for_model(obj), object_id=obj.id)
        return JsonResponse({'message': 'liked successfully'}, status=status.HTTP_200_OK)


class LikeListAPIView(generics.ListAPIView):
    serializer_class = LikeListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CommonCursorPagination

    def get_queryset(self):
        if self.kwargs['object_type'] == 'posts':
            obj = get_object_or_404(Post, id=self.kwargs['object_id'])
        elif self.kwargs['object_type'] == 'comments':
            obj = get_object_or_404(Comment, id=self.kwargs['object_id'])
        elif self.kwargs['object_type'] == 'replies':
            obj = get_object_or_404(Reply, id=self.kwargs['object_id'])
        else:
            raise InvalidObjectTypeException()

        return obj.likes
