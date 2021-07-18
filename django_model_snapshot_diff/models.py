from django.db import models
from .mixins import SnapshotMixin


class SnapshotModel(SnapshotMixin, models.Model):
    snapshot = models.JSONField(blank=True, null=True)

    class Meta:
        abstract = True
