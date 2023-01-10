import uuid
from pathlib import Path
from functools import partial
from django.db import models
from accounts.models import CustomUser


def media_directory_path(filename, forder_name):
    return f'{forder_name}/{str(uuid.uuid4())+Path(filename).suffix}'
    

    