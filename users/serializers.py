from rest_framework import serializers
from users.models import CustomUser
from phonenumber_field.serializerfields import PhoneNumberField


class CustomUserDetailsSerializer(serializers.ModelSerializer):
    phone_number = PhoneNumberField(region="KR")

    class Meta:
        model = CustomUser
        fields = (
            'id',
            'email',
            'shoe_size',
            'phone_number',
        )
        read_only_fields = ('email',)


