
from django.utils import timezone
from django.db import transaction
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from .models import Cliente, Produto, Venda, Empresa, Caixa, SessaoCaixa, Usuario
from .serializers import (
    EmpresaSerializer,
    CaixaSerializer,
    SessaoCaixaSerializer,
    ClienteSerializer,
    ProdutoSerializer,
    VendaSerializer,
    UsuarioSerializer,
)

class ClienteViewSet(ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]

class ProdutoViewSet(ModelViewSet):
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer
    permission_classes = [IsAuthenticated]

class VendaViewSet(ModelViewSet):
    queryset = Venda.objects.all()
    serializer_class = VendaSerializer
    permission_classes = [IsAuthenticated]

class EmpresaFilteredViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated or not user.empresa:
            return self.queryset.none()
        return self.queryset.filter(empresa=user.empresa)

    def perform_create(self, serializer):
        serializer.save(empresa=self.request.user.empresa)

    def perform_update(self, serializer):
        serializer.save(empresa=self.request.user.empresa)

class EmpresaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'], url_path='dados-iniciais')
    def dados_iniciais(self, request, pk=None):
        try:
            empresa = self.get_object()
            if not request.user.is_superuser and (not request.user.is_authenticated or request.user.empresa != empresa):
                return Response({'detail': 'Não autorizado a acessar dados desta empresa.'}, status=status.HTTP_403_FORBIDDEN)
            clientes = Cliente.objects.filter(empresa=empresa)
            produtos = Produto.objects.filter(empresa=empresa)
            caixas = Caixa.objects.filter(empresa=empresa)
            usuarios = Usuario.objects.filter(empresa=empresa, is_active=True)

            data = {
                'empresa': EmpresaSerializer(empresa).data,
                'clientes': ClienteSerializer(clientes, many=True).data,
                'produtos': ProdutoSerializer(produtos, many=True).data,
                'caixas': CaixaSerializer(caixas, many=True).data,
                'usuarios': UsuarioSerializer(usuarios, many=True).data,
                'current_server_time': timezone.now().timestamp()
            }
            return Response(data)
        except Empresa.DoesNotExist:
            return Response({'detail': 'Empresa não encontrada.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'], url_path='dados-atualizados')
    def dados_atualizados(self, request, pk=None):
        try:
            empresa = self.get_object()
            if not request.user.is_superuser and (not request.user.is_authenticated or request.user.empresa != empresa):
                return Response({'detail': 'Não autorizado a acessar dados desta empresa.'}, status=status.HTTP_403_FORBIDDEN)
            
            last_sync_timestamp = request.query_params.get('last_sync_timestamp')
            
            if not last_sync_timestamp:
                return Response({'detail': 'Parâmetro "last_sync_timestamp" é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                last_sync_dt = timezone.datetime.fromtimestamp(float(last_sync_timestamp), tz=timezone.utc)
            except ValueError:
                return Response({'detail': 'Formato de timestamp inválido. Deve ser um número unix timestamp.'}, status=status.HTTP_400_BAD_REQUEST)
            
            updated_clientes = Cliente.objects.filter(empresa=empresa).filter(
                models.Q(criado_em__gt=last_sync_dt) | models.Q(atualizado_em__gt=last_sync_dt)
            )
            updated_produtos = Produto.objects.filter(empresa=empresa).filter(
                models.Q(criado_em__gt=last_sync_dt) | models.Q(atualizado_em__gt=last_sync_dt)
            )
            updated_caixas = Caixa.objects.filter(empresa=empresa).filter(
                models.Q(criado_em__gt=last_sync_dt) | models.Q(atualizado_em__gt=last_sync_dt)
            )
            updated_usuarios = Usuario.objects.filter(empresa=empresa, is_active=True).filter(
                models.Q(date_joined__gt=last_sync_dt) | models.Q(atualizado_em__gt=last_sync_dt)
            )

            data = {
                'clientes_atualizados': ClienteSerializer(updated_clientes, many=True).data,
                'produtos_atualizados': ProdutoSerializer(updated_produtos, many=True).data,
                'caixas_atualizados': CaixaSerializer(updated_caixas, many=True).data,
                'usuarios_atualizados': UsuarioSerializer(updated_usuarios, many=True).data,
                'current_server_time': timezone.now().timestamp()
            }
            return Response(data)

        except Empresa.DoesNotExist:
            return Response({'detail': 'Empresa não encontrada.'}, status=status.HTTP_404_NOT_FOUND)

class CaixaViewSet(EmpresaFilteredViewSet):
    queryset = Caixa.objects.all()
    serializer_class = CaixaSerializer

class SessaoCaixaViewSet(EmpresaFilteredViewSet):
    queryset = SessaoCaixa.objects.all()
    serializer_class = SessaoCaixaSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(vendedor=self.request.user)
        return qs

    @action(detail=False, methods=['post'], url_path='abrir')
    def abrir_sessao(self, request):
        caixa_uuid = request.data.get('caixa_uuid')
        saldo_inicial = request.data.get('saldo_inicial', 0.00)
        
        if not caixa_uuid:
            return Response({'detail': 'UUID do caixa é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            caixa = Caixa.objects.get(uuid=caixa_uuid, empresa=request.user.empresa)
        except Caixa.DoesNotExist:
            return Response({'detail': 'Caixa não encontrado ou não pertence a sua empresa.'}, status=status.HTTP_404_NOT_FOUND)

        if not caixa.ativo:
            return Response({'detail': 'Caixa inativo.'}, status=status.HTTP_400_BAD_REQUEST)

        if SessaoCaixa.objects.filter(caixa=caixa, data_fechamento__isnull=True).exists():
            return Response({'detail': 'Já existe uma sessão aberta para este caixa.'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            sessao = SessaoCaixa.objects.create(
                caixa=caixa,
                vendedor=request.user,
                saldo_inicial=saldo_inicial
            )
            request.user.caixa_atual = sessao.caixa
            request.user.save()

        serializer = self.get_serializer(sessao)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='fechar')
    def fechar_sessao(self, request, pk=None):
        try:
            sessao = self.get_object() 
        except SessaoCaixa.DoesNotExist:
            return Response({'detail': 'Sessão de caixa não encontrada.'}, status=status.HTTP_404_NOT_FOUND)
        
        if sessao.vendedor != request.user and not request.user.is_staff:
             return Response({'detail': 'Não autorizado a fechar esta sessão.'}, status=status.HTTP_403_FORBIDDEN)

        if not sessao.esta_aberta:
            return Response({'detail': 'Sessão já está fechada.'}, status=status.HTTP_400_BAD_REQUEST)

        saldo_final = request.data.get('saldo_final')
        if saldo_final is None:
            return Response({'detail': 'Saldo final é obrigatório para fechar a sessão.'}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            sessao.fechar_sessao(saldo_final=saldo_final)
            if request.user.caixa_atual == sessao.caixa:
                request.user.caixa_atual = None
                request.user.save()

        serializer = self.get_serializer(sessao)
        return Response(serializer.data)

class ClienteViewSet(EmpresaFilteredViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

class ProdutoViewSet(EmpresaFilteredViewSet):
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer

class VendaViewSet(EmpresaFilteredViewSet):
    queryset = Venda.objects.all()
    serializer_class = VendaSerializer

    def create(self, request, *args, **kwargs):
        sessao_caixa_uuid = request.data.get('sessao_caixa_uuid')
        cliente_uuid = request.data.get('cliente_uuid')
        if not all([sessao_caixa_uuid, cliente_uuid]):
            return Response({'detail': 'UUIDs de sessão de caixa e cliente são obrigatórios.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            sessao_caixa = SessaoCaixa.objects.get(
                uuid=sessao_caixa_uuid, 
                vendedor=request.user,
                caixa__empresa=request.user.empresa
            )
            cliente = Cliente.objects.get(uuid=cliente_uuid, empresa=request.user.empresa)

            if not sessao_caixa.esta_aberta:
                return Response({'detail': 'Sessão de caixa não está aberta.'}, status=status.HTTP_400_BAD_REQUEST)
        
        except (SessaoCaixa.DoesNotExist, Cliente.DoesNotExist):
            return Response({'detail': 'Dados relacionados (sessão, cliente) inválidos ou não pertencem à sua empresa/usuário.'}, status=status.HTTP_400_BAD_REQUEST)
        
        mutable_data = request.data.copy()
        mutable_data['sessao_caixa'] = sessao_caixa.pk
        mutable_data['cliente'] = cliente.pk
        mutable_data['vendedor'] = request.user.pk
        mutable_data['empresa'] = request.user.empresa.pk
        serializer = self.get_serializer(data=mutable_data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            venda = serializer.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['get'], url_path='vendas-abertas-sessao')
    def vendas_abertas_sessao(self, request):
        user = request.user
        if not user.is_authenticated or not user.caixa_atual:
            return Response({'detail': 'Usuário não tem uma sessão de caixa ativa.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            current_session = SessaoCaixa.objects.get(
                caixa=user.caixa_atual,
                vendedor=user,
                data_fechamento__isnull=True
            )
            sales = Venda.objects.filter(sessao_caixa=current_session).order_by('-data_venda')
            serializer = self.get_serializer(sales, many=True)
            return Response(serializer.data)
        except SessaoCaixa.DoesNotExist:
            return Response({'detail': 'Nenhuma sessão de caixa aberta encontrada para este usuário.'}, status=status.HTTP_404_NOT_FOUND)
