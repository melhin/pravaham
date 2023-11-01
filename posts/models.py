from django.contrib.postgres.fields import ArrayField
from django.db import models

from commons.db_mixins import CommonAbstractModel


class Post(CommonAbstractModel):
    text = models.TextField()
    tags = ArrayField(base_field=models.TextField(), default=list)
