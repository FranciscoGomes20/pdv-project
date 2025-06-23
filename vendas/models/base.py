# models/base.py
from django.db import models
from django.utils import timezone
from django.conf import settings
from ..middleware import get_current_user
import uuid


class TimestampedModel(models.Model):
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class SoftDeleteModel(models.Model):
    deletado_em = models.DateTimeField(null=True, blank=True)

    def delete(self, using=None, keep_parents=False):
        self.deletado_em = timezone.now()
        self.save()

    def hard_delete(self, using=None, keep_parents=False):
        super().delete(using, keep_parents)

    class Meta:
        abstract = True

class AuditModel(models.Model):
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

class BaseModel(TimestampedModel, SoftDeleteModel, AuditModel):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    class Meta:
        abstract = True
