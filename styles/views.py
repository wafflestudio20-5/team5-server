from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from styles.models import Profile, Follow
from styles.serializers import ProfileSerializer
from styles.permissions import IsProfileOwnerOrReadOnly


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsProfileOwnerOrReadOnly]

    # def get_permissions(self):
    #     if self.action in ('list', 'retrieve'):
    #         return [IsAdminUser]
    #
    #     super().get_permissions()


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def follow(request, **kwargs):
    user = request.user
    from_profile = Profile.objects.get(user=user)
    to_profile = get_object_or_404(Profile, pk=kwargs['user'])
    try:
        follow_instance = Follow.objects.get(from_profile=from_profile, to_profile=to_profile)
        follow_instance.delete()
        return HttpResponse('successfully unfollowed', status=status.HTTP_200_OK)
    except Follow.DoesNotExist:
        Follow.objects.create(from_profile=from_profile, to_profile=to_profile)
        return HttpResponse('successfully followed', status=status.HTTP_200_OK)
