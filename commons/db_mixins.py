import uuid

from django.db import models
from django.utils import timezone


class CommonAbstractModel(models.Model):
    uuid = models.UUIDField(
        unique=True,
        db_index=True,
        verbose_name="uuid",
        default=uuid.uuid4,
        editable=False,
    )
    created_at = models.DateTimeField(verbose_name="created_at", default=timezone.now, editable=False)
    updated_at = models.DateTimeField(verbose_name="updated_at", auto_now=True)

    class Meta:
        abstract = True
