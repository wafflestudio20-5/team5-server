from django.urls import path, include
from dj_rest_auth.registration.views import VerifyEmailView, ConfirmEmailView
from dj_rest_auth.views import LoginView
from accounts.views import google_auth, naver_auth, quit_user

urlpatterns = [
    path('registration/account-confirm-email/<str:key>/', ConfirmEmailView.as_view()),
    path('registration/', include('dj_rest_auth.registration.urls'), name='registration'),
    path('account-confirm-email/', VerifyEmailView.as_view(), name='account_email_verification_sent'),
    path('login/', LoginView.as_view(), name='login'),
    path('quit/', quit_user, name='quit'),
    path('', include('dj_rest_auth.urls')),
    path('social/google/', google_auth, name='google_auth'),
    path('social/naver/', naver_auth, name='naver_auth'),
]
