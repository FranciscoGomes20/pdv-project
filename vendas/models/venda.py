from django.db import models
from .base import BaseModel
from .cliente import Cliente
from .produto import Produto
from .empresa import Empresa

class Venda(BaseModel):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    data_venda = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Venda #{self.id} - {self.cliente.nome}"


class ItemVenda(BaseModel):
    venda = models.ForeignKey(Venda, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantidade} x {self.produto.nome}"


class DevolucaoItemVenda(BaseModel):
    item_venda = models.ForeignKey(ItemVenda, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()
    motivo = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Devolução de {self.quantidade} x {self.item_venda.produto.nome}"


class Fatura(BaseModel):
    venda = models.OneToOneField(Venda, on_delete=models.CASCADE)
    data_emissao = models.DateField()
    data_vencimento = models.DateField()
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    paga = models.BooleanField(default=False)

    def __str__(self):
        return f"Fatura #{self.id} - Venda #{self.venda.id}"
