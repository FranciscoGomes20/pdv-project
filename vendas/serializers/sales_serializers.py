from rest_framework import serializers
from django.db import transaction
from ..models import Venda, ItemVenda, Fatura, DevolucaoItemVenda, Cliente, Produto, SessaoCaixa, Usuario

class ItemVendaSerializer(serializers.ModelSerializer):
    produto_uuid = serializers.UUIDField(write_only=True, required=True)
    produto_nome = serializers.CharField(source='produto.nome', read_only=True)

    class Meta:
        model = ItemVenda
        fields = ['uuid', 'produto_uuid', 'produto_nome', 'quantidade', 'preco_unitario', 'criado_em', 'atualizado_em']
        read_only_fields = ['uuid', 'criado_em', 'atualizado_em', 'produto_nome', 'preco_unitario']

    def validate_produto_uuid(self, value):
        try:
            produto = Produto.objects.get(uuid=value)
            self.context['product_objects'][str(value)] = produto 
            return value
        except Produto.DoesNotExist:
            raise serializers.ValidationError(f"Produto com o UUID '{value}' fornecido não existe.")

class FaturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fatura
        fields = ['uuid', 'data_emissao', 'data_vencimento', 'valor_total', 'paga', 'criado_em', 'atualizado_em']
        read_only_fields = ['uuid', 'criado_em', 'atualizado_em', 'valor_total']

class DevolucaoItemVendaSerializer(serializers.ModelSerializer):
    item_venda_uuid = serializers.UUIDField(write_only=True, required=True) 
    item_venda_nome = serializers.CharField(source='item_venda.produto.nome', read_only=True)

    class Meta:
        model = DevolucaoItemVenda
        fields = ['uuid', 'item_venda_uuid', 'item_venda_nome', 'quantidade', 'motivo', 'criado_em', 'atualizado_em']
        read_only_fields = ['uuid', 'criado_em', 'atualizado_em', 'item_venda_nome']

    def validate_item_venda_uuid(self, value):
        try:
            item_venda = ItemVenda.objects.get(uuid=value)
            self.context['item_venda_objects'][str(value)] = item_venda
            return value
        except ItemVenda.DoesNotExist:
            raise serializers.ValidationError(f"Item de venda com o UUID '{value}' fornecido não existe.")

class VendaSerializer(serializers.ModelSerializer):
    itens = ItemVendaSerializer(many=True, required=False)
    fatura = FaturaSerializer(required=False, allow_null=True)
    devolucoes = DevolucaoItemVendaSerializer(many=True, required=False)
    cliente_nome = serializers.CharField(source='cliente.nome', read_only=True)
    vendedor_username = serializers.CharField(source='vendedor.username', read_only=True)
    caixa_nome = serializers.CharField(source='sessao_caixa.caixa.nome', read_only=True)
    cliente_uuid = serializers.UUIDField(write_only=True, required=True)
    vendedor_uuid = serializers.UUIDField(write_only=True, required=True)
    sessao_caixa_uuid = serializers.UUIDField(write_only=True, required=True)

    class Meta:
        model = Venda
        fields = [
            'uuid', 'empresa', 'cliente', 'cliente_uuid', 'sessao_caixa', 'sessao_caixa_uuid',
            'vendedor', 'vendedor_uuid', 'data_venda', 'total',
            'itens', 'fatura', 'devolucoes',
            'cliente_nome', 'vendedor_username', 'caixa_nome',
            'criado_em', 'atualizado_em'
        ]
        read_only_fields = [
            'uuid', 'empresa', 'cliente', 'sessao_caixa', 'vendedor',
            'data_venda', 'total',
            'cliente_nome', 'vendedor_username', 'caixa_nome',
            'criado_em', 'atualizado_em'
        ]

    def create(self, validated_data):
        itens_data = validated_data.pop('itens', [])
        fatura_data = validated_data.pop('fatura', None)
        devolucoes_data = validated_data.pop('devolucoes', [])
        cliente_uuid = validated_data.pop('cliente_uuid')
        vendedor_uuid = validated_data.pop('vendedor_uuid')
        sessao_caixa_uuid = validated_data.pop('sessao_caixa_uuid')

        try:
            cliente = Cliente.objects.get(uuid=cliente_uuid)
            vendedor = Usuario.objects.get(uuid=vendedor_uuid)
            sessao_caixa = SessaoCaixa.objects.get(uuid=sessao_caixa_uuid)
            empresa = sessao_caixa.caixa.empresa 

        except (Cliente.DoesNotExist, Usuario.DoesNotExist, SessaoCaixa.DoesNotExist) as e:
            raise serializers.ValidationError(f"Erro de dados relacionados: {e}")

        validated_data['cliente'] = cliente
        validated_data['vendedor'] = vendedor
        validated_data['sessao_caixa'] = sessao_caixa
        validated_data['empresa'] = empresa

        total_venda = 0
        for item_data in itens_data:
            product_obj = self.context['product_objects'][str(item_data['produto_uuid'])]
            total_venda += product_obj.preco * item_data['quantidade']
        validated_data['total'] = total_venda

        with transaction.atomic():
            venda = Venda.objects.create(**validated_data)

            for item_data in itens_data:
                product_obj = self.context['product_objects'][str(item_data['produto_uuid'])]
                ItemVenda.objects.create(
                    venda=venda,
                    produto=product_obj,
                    quantidade=item_data['quantidade'],
                    preco_unitario=product_obj.preco
                )
                product_obj.estoque -= item_data['quantidade']
                product_obj.save()

            if fatura_data:
                if 'valor_total' not in fatura_data:
                     fatura_data['valor_total'] = total_venda
                Fatura.objects.create(venda=venda, **fatura_data)
            
            for devolucao_data in devolucoes_data:
                item_venda_obj = self.context['item_venda_objects'][str(devolucao_data['item_venda_uuid'])]
                DevolucaoItemVenda.objects.create(
                    venda=venda,
                    item_venda=item_venda_obj,
                    quantidade=devolucao_data['quantidade'],
                    motivo=devolucao_data['motivo']
                )
        return venda
    
    def update(self, instance, validated_data):
        itens_data = validated_data.pop('itens', None)
        fatura_data = validated_data.pop('fatura', None)
        devolucoes_data = validated_data.pop('devolucoes', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        with transaction.atomic():
            if itens_data is not None:
                current_items = instance.itens.all()
                for item in current_items:
                    item.produto.estoque += item.quantidade
                    item.produto.save()
                current_items.delete()

                for item_data in itens_data:
                    product_obj = self.context['product_objects'][str(item_data['produto_uuid'])]
                    ItemVenda.objects.create(
                        venda=instance,
                        produto=product_obj,
                        quantidade=item_data['quantidade'],
                        preco_unitario=product_obj.preco
                    )
                    product_obj.estoque -= item_data['quantidade']
                    product_obj.save()
                
                instance.total = sum((item.produto.preco * item.quantidade) for item in instance.itens.all())
                instance.save()

            if fatura_data is not None:
                if hasattr(instance, 'fatura') and instance.fatura:
                    for attr, value in fatura_data.items():
                        setattr(instance.fatura, attr, value)
                    instance.fatura.save()
                else:
                    if 'valor_total' not in fatura_data:
                        fatura_data['valor_total'] = instance.total
                    Fatura.objects.create(venda=instance, **fatura_data)
            
            if devolucoes_data is not None:
                for devolucao_data in devolucoes_data:
                    item_venda_obj = self.context['item_venda_objects'][str(devolucao_data['item_venda_uuid'])]
                    DevolucaoItemVenda.objects.create(
                        venda=instance,
                        item_venda=item_venda_obj,
                        quantidade=devolucao_data['quantidade'],
                        motivo=devolucao_data['motivo']
                    )

        return instance

    def run_validation(self, data):
        self.context['product_objects'] = {}
        self.context['item_venda_objects'] = {}

        for item_data in data.get('itens', []):
            if 'produto_uuid' in item_data:
                pass 

        for devolucao_data in data.get('devolucoes', []):
            if 'item_venda_uuid' in devolucao_data:
                pass
        return super().run_validation(data)