from django.dispatch import receiver
from django.db.models.signals import post_delete

from styles.models import PostImage


@receiver(post_delete, sender=PostImage)
def remove_file_from_s3(sender, instance: PostImage, using, **kwargs):
    instance.image.delete(save=False)
