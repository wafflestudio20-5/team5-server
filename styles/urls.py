from django.urls import path
from styles import views

urlpatterns = [
    path('profiles/<pk>/', views.ProfileDetailView.as_view(), name='profile-detail'),
    path('profiles/<int:user>/followers/', views.FollowerListView.as_view(), name='followers'),
    path('profiles/<int:user>/followings/', views.FollowingListView.as_view(), name='followings'),
    path('profiles/<int:user>/follow/', views.follow, name='profile-follow'),
]
