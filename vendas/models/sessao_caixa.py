from django.db import models
from django.utils import timezone
from .base import BaseModel
from .caixa import Caixa
from .usuario import Usuario

class SessaoCaixa(BaseModel):
    caixa = models.ForeignKey(Caixa, on_delete=models.PROTECT, related_name='sessoes')
    vendedor = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='sessoes_caixa_iniciadas')
    data_abertura = models.DateTimeField(default=timezone.now)
    data_fechamento = models.DateTimeField(null=True, blank=True)
    saldo_inicial = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Valor em caixa ao iniciar a sessão.")
    saldo_final = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Valor em caixa ao fechar a sessão.")
    observacoes = models.TextField(blank=True, null=True, help_text="Observações sobre a sessão do caixa.")

    class Meta:
        verbose_name = "Sessão de Caixa"
        verbose_name_plural = "Sessões de Caixa"
        ordering = ['-data_abertura'] # Ordena pelas sessões mais recentes

    def __str__(self):
        status = "Aberta" if not self.data_fechamento else "Fechada"
        return f"Sessão {self.uuid.hex[:8]} - {self.caixa.nome} - {self.vendedor.username} ({status})"

    # Propriedade para verificar se a sessão está aberta
    @property
    def esta_aberta(self):
        return self.data_fechamento is None

    # Método para fechar a sessão, se necessário (pode ser chamado via API)
    def fechar_sessao(self, saldo_final=None):
        if self.esta_aberta:
            self.data_fechamento = timezone.now()
            if saldo_final is not None:
                self.saldo_final = saldo_final
            self.save()
            return True
        return False