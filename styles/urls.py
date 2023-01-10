from django.urls import path
from styles import views

urlpatterns = [
    path('profiles/', views.ProfileViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='profile-list'),
    path('profiles/<pk>/', views.ProfileViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'update',
        'delete': 'destroy'
    }), name='profile-detail'),
    path('profiles/<int:user>/follow/', views.follow, name='profile-follow'),
]
