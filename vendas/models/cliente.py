import uuid
from django.db import models
from .base import BaseModel
from .empresa import Empresa

class Cliente(BaseModel):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14)
    email = models.EmailField(blank=True, null=True)
    telefone = models.CharField(max_length=15, blank=True, null=True)
    endereco = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('empresa', 'cpf')
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    def __str__(self):
        return self.nome