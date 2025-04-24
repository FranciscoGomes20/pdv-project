# Create your views here.
from rest_framework.viewsets import ModelViewSet
from .models import Cliente, Produto, Venda, ItemVenda
from .serializers import ClienteSerializer, ProdutoSerializer, VendaSerializer, ItemVendaSerializer

class ClienteViewSet(ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

class ProdutoViewSet(ModelViewSet):
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer

class VendaViewSet(ModelViewSet):
    queryset = Venda.objects.all()
    serializer_class = VendaSerializer

class ItemVendaViewSet(ModelViewSet):
    queryset = ItemVenda.objects.all()
    serializer_class = ItemVendaSerializer
