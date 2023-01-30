import os
from uuid import uuid4

from django.utils import timezone


def get_media_path(instance, filename, dir_name):
    ymd_path = timezone.now().strftime('%Y/%m/%d')
    upload_to = dir_name + '/' + ymd_path
    ext = filename.split('.')[-1]
    uuid = uuid4().hex

    filename = '{}_{}.{}'.format(uuid, instance, ext)

    return os.path.join(upload_to, filename)
