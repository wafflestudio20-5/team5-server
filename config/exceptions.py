from rest_framework import status
from rest_framework.exceptions import APIException


class InvalidObjectTypeException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'invalid object type'
    default_code = 'invalid_object_type'