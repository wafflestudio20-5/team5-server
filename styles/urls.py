from django.urls import path
from styles import views

urlpatterns = [
    path('profiles/', views.ProfileListAPIView.as_view()),
    path('profiles/<int:user_id>/', views.ProfileRetrieveUpdateAPIView.as_view()),
    path('profiles/<int:user_id>/followers/', views.FollowerListAPIView.as_view()),
    path('profiles/<int:user_id>/followings/', views.FollowingListAPIView.as_view()),
    path('profiles/<int:user_id>/follow/', views.follow, name='follow/unfollow'),
    path('posts/', views.PostListCreateAPIView.as_view()),
    path('posts/<int:post_id>/', views.PostRetrieveUpdateDestroyAPIView.as_view()),
    path('posts/<int:post_id>/comments/', views.CommentListCreateAPIView.as_view(), name='post-comment-list'),
    path('comments/<int:comment_id>/', views.CommentListCreateAPIView.as_view(), name='post-comment-list'),
    path('comments/<int:comment_id>/replies/', views.CommentListCreateAPIView.as_view(), name='post-comment-list'),
    path('replies/<int:reply_id>/', views.CommentListCreateAPIView.as_view(), name='post-comment-list'),
]
