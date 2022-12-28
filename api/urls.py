from django.urls import path, include
from dj_rest_auth.registration.views import VerifyEmailView, ConfirmEmailView
from dj_rest_auth.views import LoginView

urlpatterns = [
    path('dj-rest-auth/registration/account-confirm-email/<str:key>/', ConfirmEmailView.as_view()),
    path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    path('dj-rest-auth/account-confirm-email/', VerifyEmailView.as_view(), name='account_email_verification_sent'),
    path('dj-rest-auth/login/', LoginView.as_view(), name='login'),
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
]
