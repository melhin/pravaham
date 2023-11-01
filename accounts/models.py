from django.contrib.auth.models import AbstractUser
from django.db import models

from commons.db_mixins import CommonAbstractModel


class User(AbstractUser, CommonAbstractModel):
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    username = None
    email = models.EmailField(unique=True)

    def __str__(self):
        return str(self.uuid)

    def __repr__(self):
        return f"{self.__class__.__name__}: {self.email}"