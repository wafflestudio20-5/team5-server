from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from dj_rest_auth.serializers import LoginSerializer
from dj_rest_auth.registration.serializers import RegisterSerializer
from django.contrib.auth import authenticate, get_user_model
from rest_framework import exceptions, serializers
from config.settings import base


class CustomLoginSerializer(LoginSerializer):
    username = None

    def authenticate(self, **kwargs):
        return authenticate(self.context["request"], **kwargs)

    def validate(self, attrs):
        username = None
        email = attrs.get('email')
        password = attrs.get('password')
        user = self.get_auth_user(username, email, password)
        if not user:
            msg = 'Unable to log in with provided credentials.'
            raise exceptions.ValidationError(msg)

        # Did we get back an active user?
        self.validate_auth_user_status(user)

        # If required, is the email verified?
        if 'dj_rest_auth.registration' in base.INSTALLED_APPS:
            self.validate_email_verification_status(user)

        attrs['user'] = user
        return attrs


SIZE_CHOICES = [(220+5*i, 220+5*i)for i in range(17)]
class CustomRegisterSerializer(RegisterSerializer):
    username = None
    shoe_size = serializers.ChoiceField(choices=SIZE_CHOICES)

    class Meta:
        model = get_user_model()
        fields = (
            'id',
            'email',
            'password',
            'shoe_size',
            'phone_number',
        )

    def get_cleaned_data(self):
        return {
            "email": self.validated_data.get("email", ""),
            'password1': self.validated_data.get('password1', ''),
            'password2': self.validated_data.get('password2', ''),
            "phone_number": self.validated_data.get("phone_number", ''),
            "shoe_size": self.validated_data.get("shoe_size")
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        setup_user_email(request, user, [])
        user.phone_number = self.cleaned_data.get("phone_number")
        user.shoe_size = self.cleaned_data.get("shoe_size")
        user.save()
        adapter.save_user(request, user, self)
        return user
