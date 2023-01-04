import jwt
import requests
from django.http import JsonResponse
from rest_framework import status

from config.settings.base import config_secret_common, SIMPLE_JWT
from .models import *

SECRET_KEY = config_secret_common['django']['secret_key']
ALGORITHM = SIMPLE_JWT['ALGORITHM']


# TODO: REFRESH TOKEN 생성


def google_auth(request):
    access_token = request.GET.get('token', None)
    user_req = requests.get(f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}")
    return _auth(user_req)


def naver_auth(request):
    access_token = request.GET.get('token', None)
    user_req = requests.get(url="https://openapi.naver.com/v1/nid/me",
                            headers={"Authorization": f"Bearer {access_token}"})
    return _auth(user_req)


def _auth(user_req):
    user_req_status = user_req.status_code

    if user_req_status != 200:
        return JsonResponse({'err_msg': 'failed to get user information'}, status=status.HTTP_400_BAD_REQUEST)

    user_req_json = user_req.json()
    email = user_req_json.get('email')

    try:
        user = CustomUser.objects.get(email=email)
        jwt_token = jwt.encode({'id': user.id}, SECRET_KEY, ALGORITHM)
        return JsonResponse({'token': jwt_token, 'exist': True})

    except CustomUser.DoesNotExist:
        CustomUser(email=email).save()
        user = CustomUser.objects.get(email=email)
        jwt_token = jwt.encode({'id': user.id}, SECRET_KEY, ALGORITHM)
        return JsonResponse({'token': jwt_token, 'exist': False})
