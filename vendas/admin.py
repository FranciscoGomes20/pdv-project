from django.contrib import admin
from .models import Cliente, Produto, Venda, ItemVenda


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cpf', 'email', 'telefone', 'criado_em', 'atualizado_em')
    search_fields = ('nome', 'cpf', 'email')
    list_filter = ('criado_em',)

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'preco', 'estoque', 'criado_em', 'atualizado_em')
    search_fields = ('nome',)
    list_filter = ('criado_em',)

class ItemVendaInline(admin.TabularInline):
    model = ItemVenda
    extra = 1  # número de linhas extras em branco
    readonly_fields = ('subtotal',)

    def subtotal(self, obj):
        return obj.quantidade * obj.produto.preco if obj.produto else 0
    subtotal.short_description = 'Subtotal'

@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'data_venda', 'total', 'criado_em', 'atualizado_em')
    search_fields = ('cliente__nome',)
    list_filter = ('data_venda', 'criado_em')
    inlines = [ItemVendaInline]

@admin.register(ItemVenda)
class ItemVendaAdmin(admin.ModelAdmin):
    list_display = ('venda', 'produto', 'quantidade', 'subtotal')
    search_fields = ('venda__id', 'produto__nome')
    list_filter = ('venda__data_venda',)

    def subtotal(self, obj):
        return obj.quantidade * obj.produto.preco
    subtotal.short_description = 'Subtotal'
