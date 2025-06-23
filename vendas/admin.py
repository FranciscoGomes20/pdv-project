from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Cliente, Produto, Venda, ItemVenda, DevolucaoItemVenda, Fatura, Usuario, Empresa, Caixa, SessaoCaixa

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cnpj', 'ativa', 'criado_em', 'atualizado_em')
    list_filter = ('ativa', 'criado_em')
    search_fields = ('nome', 'cnpj')
    class UsuarioInline(admin.TabularInline):
         model = Usuario
         extra = 0
         fields = ('username', 'email', 'is_active')
    class CaixaInline(admin.TabularInline):
         model = Caixa
         extra = 0
         fields = ('nome', 'tipo', 'ativo')
    inlines = [UsuarioInline, CaixaInline]

# --- Configuração do Admin para o Modelo Cliente ---
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cpf', 'email', 'telefone', 'empresa', 'criado_em', 'atualizado_em')
    search_fields = ('nome', 'cpf', 'email')
    list_filter = ('empresa', 'criado_em')
    raw_id_fields = ('empresa',)

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'preco', 'estoque', 'empresa', 'criado_em', 'atualizado_em')
    search_fields = ('nome',)
    list_filter = ('empresa', 'criado_em')
    raw_id_fields = ('empresa',)

@admin.register(Caixa)
class CaixaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'empresa', 'tipo', 'ativo', 'ip_endereco', 'porta', 'criado_em', 'atualizado_em')
    list_filter = ('empresa', 'tipo', 'ativo')
    search_fields = ('nome', 'ip_endereco')
    raw_id_fields = ('empresa',)

    class SessaoCaixaInline(admin.TabularInline):
        model = SessaoCaixa
        extra = 0
        fields = ('vendedor', 'data_abertura', 'data_fechamento', 'saldo_inicial', 'saldo_final')
        readonly_fields = fields
        show_change_link = True 
    inlines = [SessaoCaixaInline]

@admin.register(SessaoCaixa)
class SessaoCaixaAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'caixa', 'vendedor', 'data_abertura', 'data_fechamento', 'esta_aberta', 'saldo_inicial', 'saldo_final')
    list_filter = ('caixa__empresa', 'caixa', 'vendedor', 'data_abertura', 'data_fechamento')
    search_fields = ('uuid__icontains', 'caixa__nome', 'vendedor__username')
    raw_id_fields = ('caixa', 'vendedor')
    readonly_fields = ('uuid', 'data_abertura')

    class VendaInline(admin.TabularInline):
        model = Venda
        extra = 0
        fields = ('uuid', 'cliente', 'data_venda', 'total', 'criado_por')
        readonly_fields = fields
        show_change_link = True

    inlines = [VendaInline]

class ItemVendaInline(admin.TabularInline):
    model = ItemVenda
    extra = 1
    fields = ('produto', 'quantidade', 'preco_unitario', 'subtotal')
    readonly_fields = ('subtotal',)

    def subtotal(self, obj):
        return obj.quantidade * obj.preco_unitario
    subtotal.short_description = 'Subtotal'

class FaturaInline(admin.StackedInline): 
    model = Fatura
    extra = 0
    max_num = 1
    fields = ('data_emissao', 'data_vencimento', 'valor_total', 'paga')

class DevolucaoItemVendaInline(admin.TabularInline):
    model = DevolucaoItemVenda
    extra = 0
    fields = ('item_venda', 'quantidade', 'motivo')
    raw_id_fields = ('item_venda',)

@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'empresa', 'cliente', 'vendedor', 'sessao_caixa', 'data_venda', 'total', 'criado_por', 'atualizado_em')
    list_filter = ('empresa', 'sessao_caixa__caixa', 'vendedor', 'data_venda', 'criado_em')
    search_fields = ('uuid__icontains', 'cliente__nome', 'sessao_caixa__caixa__nome', 'vendedor__username')
    raw_id_fields = ('empresa', 'cliente', 'vendedor', 'sessao_caixa')
    inlines = [ItemVendaInline, FaturaInline, DevolucaoItemVendaInline]

@admin.register(ItemVenda)
class ItemVendaAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'venda', 'produto', 'quantidade', 'preco_unitario', 'subtotal')
    search_fields = ('uuid__icontains', 'venda__id', 'produto__nome')
    list_filter = ('venda__data_venda', 'produto__empresa')
    raw_id_fields = ('venda', 'produto')

    def subtotal(self, obj):
        return obj.quantidade * obj.preco_unitario
    subtotal.short_description = 'Subtotal'

@admin.register(Fatura)
class FaturaAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'venda', 'data_emissao', 'data_vencimento', 'valor_total', 'paga')
    list_filter = ('paga', 'data_emissao', 'data_vencimento', 'venda__empresa')
    search_fields = ('uuid__icontains', 'venda__id')
    raw_id_fields = ('venda',)

@admin.register(DevolucaoItemVenda)
class DevolucaoItemVendaAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'item_venda', 'quantidade', 'motivo', 'criado_em')
    list_filter = ('criado_em', 'item_venda__venda__empresa')
    search_fields = ('uuid__icontains', 'item_venda__venda__id', 'motivo')
    raw_id_fields = ('item_venda',)

class UsuarioAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        (('Informações da Empresa e Caixa', {'fields': ('empresa', 'caixa_atual')}),)
    )
    list_display = BaseUserAdmin.list_display + ('empresa', 'caixa_atual',)
    list_filter = BaseUserAdmin.list_filter + ('empresa', 'caixa_atual',)

try:
    admin.site.unregister(Usuario)
except admin.sites.NotRegistered:
    pass
admin.site.register(Usuario, UsuarioAdmin)
