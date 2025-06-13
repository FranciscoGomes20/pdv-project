from django.contrib.auth.models import AbstractUser
from django.db import models
from .empresa import Empresa

class Usuario(AbstractUser):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.username
