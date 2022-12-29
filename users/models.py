from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField

from .managers import CustomUserManager


SIZE_CHOICES = [(220+5*i, 220+5*i)for i in range(19)]


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    shoe_size = models.CharField(choices=SIZE_CHOICES, blank=True, default="", max_length=3)
    phone_number = PhoneNumberField(blank=True)


# class Profile(models.Model):
#     user = models.ForeignKey()
