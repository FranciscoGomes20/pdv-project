from django.db import models
from .base import BaseModel
from .empresa import Empresa

class TipoCaixa(models.TextChoices):
    PRINCIPAL = 'PRIN', 'Caixa Principal'
    SATELITE = 'SAT', 'Caixa Satélite'

class Caixa(BaseModel):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100, help_text="Ex: Caixa 1, Terminal Principal")
    ativo = models.BooleanField(default=True)
    
    tipo = models.CharField(
        max_length=4,
        choices=TipoCaixa.choices,
        default=TipoCaixa.SATELITE,
        help_text="Tipo de caixa: Principal (com DB local) ou Satélite (conecta ao Principal)"
    )
    
    ip_endereco = models.GenericIPAddressField(
        blank=True, null=True,
        help_text="Endereço IP do Caixa (para registro, não para conexão direta do Django central)"
    )
    porta = models.IntegerField(
        blank=True, null=True,
        help_text="Porta de serviço deste Caixa (para registro, não para conexão direta do Django central)"
    )

    class Meta:
        verbose_name = "Caixa / Terminal de Venda"
        verbose_name_plural = "Caixas / Terminais de Venda"
        unique_together = ('empresa', 'nome') 

    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"