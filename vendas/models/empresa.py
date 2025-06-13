from django.db import models
from .base import BaseModel

class Empresa(BaseModel):
    nome = models.CharField(max_length=100)
    cnpj = models.CharField(max_length=18, unique=True)
    schema_name = models.CharField(
        max_length=63,
        unique=True,
        help_text="Nome do esquema no banco de dados para esta empresa."
    )
    ativa = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Empresa (CNPJ)"
        verbose_name_plural = "Empresas (CNPJs)"