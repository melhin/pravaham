from django.contrib.postgres.fields import ArrayField
from django.db import models

from commons.db_mixins import CommonAbstractModel


class Post(CommonAbstractModel):
    text = models.TextField()
    creator = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    tags = ArrayField(base_field=models.TextField(), default=list)
