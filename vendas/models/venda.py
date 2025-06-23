from django.db import models
from .base import BaseModel
from .cliente import Cliente
from .produto import Produto
from .empresa import Empresa
from .sessao_caixa import SessaoCaixa
from .usuario import Usuario

class Venda(BaseModel):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    data_venda = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    sessao_caixa = models.ForeignKey( # <-- Nova FK para SessaoCaixa
        SessaoCaixa,
        on_delete=models.PROTECT, # Não permite apagar sessão se houver vendas
        related_name='vendas'
    )
    vendedor = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL, # Se o usuário for removido, as vendas não são deletadas
        null=True, blank=True,     # Permite vendas sem vendedor associado (caso necessário)
        related_name='vendas_como_vendedor'
    )

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
    venda = models.ForeignKey(Venda, on_delete=models.CASCADE, related_name='devolucoes_itens')

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
