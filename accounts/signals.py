from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import CustomUser
from styles.models import Profile
from uuid import uuid4


@receiver(post_save, sender=CustomUser)
def create_profile(sender, instance: CustomUser, created, **kwargs):
    if created:
        user_name = instance.email.split('@')[0]
        profile_name = uuid4().hex[:7].lower()
        while Profile.objects.filter(profile_name=profile_name).exists():
            profile_name = uuid4().hex[:7].lower()
        Profile(user=instance, user_name=user_name, profile_name=profile_name).save()
