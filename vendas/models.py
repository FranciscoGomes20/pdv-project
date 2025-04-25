from django.db import models
from django.conf import settings
from .middleware import get_current_user
from django.utils import timezone

class AuditModel(models.Model):
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        related_name="%(class)s_criado_por",
        on_delete=models.SET_NULL
    )
    atualizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        related_name="%(class)s_atualizado_por",
        on_delete=models.SET_NULL
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        user = get_current_user()
        if not self.pk:
            self.criado_por = user
        self.atualizado_por = user
        super().save(*args, **kwargs)

class Cliente(AuditModel):
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14, unique=True)
    email = models.EmailField(blank=True, null=True)
    telefone = models.CharField(max_length=15, blank=True, null=True)
    endereco = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nome

class Produto(AuditModel):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    estoque = models.IntegerField()

    def __str__(self):
        return self.nome

class Venda(AuditModel):
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True)
    data_venda = models.DateTimeField(default=timezone.now)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f'Venda #{self.pk} - {self.data_venda.strftime("%d/%m/%Y %H:%M")}'

class ItemVenda(AuditModel):
    venda = models.ForeignKey(Venda, related_name='itens', on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    quantidade = models.PositiveIntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.quantidade * self.preco_unitario

    def __str__(self):
        return f'{self.quantidade} x {self.produto.nome}'

class Fatura(AuditModel):
    venda = models.OneToOneField(Venda, on_delete=models.CASCADE)
    numero = models.CharField(max_length=20, unique=True)
    data_emissao = models.DateTimeField(default=timezone.now)
    pdf = models.FileField(upload_to='notas_fiscais/', blank=True, null=True)

    def __str__(self):
        return f'NFe {self.numero}'
