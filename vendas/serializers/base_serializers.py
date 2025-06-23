from rest_framework import serializers
from ..models import Empresa, Usuario, Caixa, Cliente, Produto, SessaoCaixa

class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = ['uuid', 'nome', 'cnpj', 'ativa', 'criado_em', 'atualizado_em']
        read_only_fields = ['uuid', 'criado_em', 'atualizado_em']

class UsuarioSerializer(serializers.ModelSerializer):
    empresa_nome = serializers.CharField(source='empresa.nome', read_only=True)
    caixa_atual_nome = serializers.CharField(source='caixa_atual.nome', read_only=True)

    class Meta:
        model = Usuario
        fields = [
            'uuid', 'username', 'email', 'first_name', 'last_name',
            'empresa', 'empresa_nome', 'caixa_atual', 'caixa_atual_nome',
            'is_staff', 'is_active', 'date_joined', 'last_login'
        ]
        read_only_fields = [
            'uuid', 'empresa', 'empresa_nome', 'caixa_atual', 'caixa_atual_nome',
            'is_staff', 'is_active', 'date_joined', 'last_login'
        ]
        extra_kwargs = {'password': {'write_only': True, 'required': False}}

class ClienteSerializer(serializers.ModelSerializer):
    empresa_nome = serializers.CharField(source='empresa.nome', read_only=True)

    class Meta:
        model = Cliente
        fields = ['uuid', 'empresa', 'empresa_nome', 'nome', 'cpf', 'email', 'telefone', 'endereco', 'criado_em', 'atualizado_em']
        read_only_fields = ['uuid', 'criado_em', 'atualizado_em']

class ProdutoSerializer(serializers.ModelSerializer):
    empresa_nome = serializers.CharField(source='empresa.nome', read_only=True)

    class Meta:
        model = Produto
        fields = ['uuid', 'empresa', 'empresa_nome', 'nome', 'descricao', 'preco', 'estoque', 'criado_em', 'atualizado_em']
        read_only_fields = ['uuid', 'criado_em', 'atualizado_em']

class CaixaSerializer(serializers.ModelSerializer):
    empresa_nome = serializers.CharField(source='empresa.nome', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)

    class Meta:
        model = Caixa
        fields = ['uuid', 'empresa', 'empresa_nome', 'nome', 'ativo', 'tipo', 'tipo_display', 'ip_endereco', 'porta', 'criado_em', 'atualizado_em']
        read_only_fields = ['uuid', 'criado_em', 'atualizado_em']

class SessaoCaixaSerializer(serializers.ModelSerializer):
    caixa_nome = serializers.CharField(source='caixa.nome', read_only=True)
    vendedor_username = serializers.CharField(source='vendedor.username', read_only=True)
    esta_aberta = serializers.BooleanField(read_only=True) 

    class Meta:
        model = SessaoCaixa
        fields = [
            'uuid', 'caixa', 'caixa_nome', 'vendedor', 'vendedor_username',
            'data_abertura', 'data_fechamento', 'saldo_inicial', 'saldo_final', 'observacoes',
            'esta_aberta', 'criado_em', 'atualizado_em'
        ]
        read_only_fields = ['uuid', 'data_abertura', 'criado_em', 'atualizado_em', 'esta_aberta']