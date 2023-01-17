from django.urls import path
from styles import views

urlpatterns = [
    path('profiles/', views.ProfileListAPIView.as_view()),
    path('profiles/<int:user_id>/', views.ProfileRetrieveUpdateAPIView.as_view()),
    path('profiles/<int:user_id>/followers/', views.FollowerListAPIView.as_view()),
    path('profiles/<int:user_id>/followings/', views.FollowingListAPIView.as_view()),
    path('profiles/<int:user_id>/follow/', views.follow, name='follow/unfollow'),
    path('posts/', views.PostListCreateAPIView.as_view()),
    path('posts/<pk>/', views.PostRetrieveUpdateDestroyAPIView.as_view()),
    path('posts/<pk>/comments/', views.CommentListCreateAPIView.as_view(), name='post-comment-list'),
    path('comments/<pk>/', views.CommentListCreateAPIView.as_view(), name='post-comment-list'),
    path('comments/<pk>/replies/', views.CommentListCreateAPIView.as_view(), name='post-comment-list'),
    path('replies/<pk>/', views.CommentListCreateAPIView.as_view(), name='post-comment-list'),
]
