from rest_framework import serializers
from .models import Cliente, Produto, Venda, ItemVenda

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'

class ProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produto
        fields = '__all__'

class ItemVendaSerializer(serializers.ModelSerializer):
    produto = ProdutoSerializer(read_only=True)
    produto_id = serializers.PrimaryKeyRelatedField(queryset=Produto.objects.all(), source='produto', write_only=True)

    class Meta:
        model = ItemVenda
        fields = ['id', 'venda', 'produto', 'produto_id', 'quantidade', 'preco_unitario', 'created_at', 'updated_at']

class VendaSerializer(serializers.ModelSerializer):
    cliente = ClienteSerializer(read_only=True)
    cliente_id = serializers.PrimaryKeyRelatedField(queryset=Cliente.objects.all(), source='cliente', write_only=True)
    itens = ItemVendaSerializer(many=True, read_only=True)

    class Meta:
        model = Venda
        fields = ['id', 'cliente', 'cliente_id', 'data_venda', 'total', 'itens', 'created_at', 'updated_at']
