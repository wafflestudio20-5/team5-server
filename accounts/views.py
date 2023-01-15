import requests
from django.contrib.auth.models import update_last_login
from django.http import JsonResponse
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import CustomUser
from accounts.serializers import CustomUserDetailsSerializer


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def google_auth(request):
    access_token = request.GET.get('token', None)
    if access_token is None:
        return JsonResponse({'err_msg': 'query parameter "token" needed'}, status=status.HTTP_400_BAD_REQUEST)

    user_req = requests.get(f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}")
    user_req_status = user_req.status_code
    if user_req_status != 200:
        return JsonResponse({'err_msg': 'failed to get user information'}, status=status.HTTP_400_BAD_REQUEST)

    user_req_json = user_req.json()
    email = user_req_json['email']
    return _auth(email)


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def naver_auth(request):
    access_token = request.GET.get('token', None)
    if access_token is None:
        return JsonResponse({'err_msg': 'query parameter "token" needed'}, status=status.HTTP_400_BAD_REQUEST)

    user_req = requests.get(url="https://openapi.naver.com/v1/nid/me",
                            headers={"Authorization": f"Bearer {access_token}"})
    user_req_status = user_req.status_code
    if user_req_status != 200:
        return JsonResponse({'err_msg': 'failed to get user information'}, status=status.HTTP_400_BAD_REQUEST)

    user_req_json = user_req.json()
    email = user_req_json['response']['email']
    return _auth(email)


def _auth(email):
    try:
        user = CustomUser.objects.get(email=email)
        tokens = _generate_tokens(user)
        _login(user)
        return JsonResponse({
            **tokens,
            'user': CustomUserDetailsSerializer(user).data,
            'exists': True
        })

    except CustomUser.DoesNotExist:
        user = CustomUser.objects.create(email=email)
        tokens = _generate_tokens(user)
        _login(user)
        return JsonResponse({
            **tokens,
            'user': CustomUserDetailsSerializer(user).data,
            'exists': False
        })


def _login(user):
    update_last_login(None, user)


def _generate_tokens(user):
    refresh = RefreshToken.for_user(user)

    return {
        'access_token': str(refresh.access_token),
        'refresh_token': str(refresh),
    }
