from django.contrib.auth.models import AbstractUser
from django.db import models
from .empresa import Empresa
from .caixa import Caixa

class Usuario(AbstractUser):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True)
    caixa_atual = models.ForeignKey(
        Caixa,
        on_delete=models.SET_NULL, 
        null=True,                 
        blank=True,                
        related_name='usuarios_com_caixa_aberto'
    )

    def __str__(self):
        return self.username
