from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import CustomUser
from styles.models import Profile


@receiver(post_save, sender=CustomUser)
def create_profile(sender, instance: CustomUser, created, **kwargs):
    if created:
        user_name = instance.email.split('@')[0]
        Profile(user=instance, user_name=user_name).save()
