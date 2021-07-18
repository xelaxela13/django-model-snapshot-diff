from django.db import models
from django_model_snapshot_diff.mixins import SnapshotMixin
from django_model_snapshot_diff.models import SnapshotModel


class ManyToMany(SnapshotMixin, models.Model):
    description = models.CharField(max_length=255)

    snapshot_fields = [
        ('description', 'ManyToMany DESCRIPTION field'),
    ]


class ForeignKeyDeeper(SnapshotMixin, models.Model):
    name = models.CharField(max_length=255)
    many_to_many = models.ManyToManyField('example.ManyToMany')

    snapshot_fields = [
        ('name', 'ForeignKeyDeeper NAME field'),
        ('many_to_many', 'ForeignKeyDeeper MANYTOMANY field'),
    ]


class ForeignKey(SnapshotMixin, models.Model):
    title = models.CharField(max_length=255)
    foreign_key_deeper = models.ForeignKey('example.ForeignKeyDeeper',
                                           on_delete=models.CASCADE)

    snapshot_fields = [
        ('title', 'ForeignKey TITLE field'),
        ('foreign_key_deeper', 'ForeignKey DEEPER field'),
    ]


class Relation(SnapshotMixin, models.Model):
    choice = models.CharField(choices=((1, 'A'), (2, 'B')), default=1,
                              max_length=2)
    rel_to_example = models.ForeignKey('example.Example',
                                       on_delete=models.CASCADE,
                                       related_name='relation_to_example')

    snapshot_fields = [
        ('choice', 'Relation CHOICE field'),
    ]


class Example(SnapshotModel):
    text = models.CharField(max_length=255)
    boolean = models.BooleanField(default=False)
    datetime = models.DateTimeField(auto_now=True)
    foreign_key = models.ForeignKey('example.ForeignKey',
                                    on_delete=models.CASCADE)

    snapshot_fields = [
        ('text', 'Example TEXT field'),
        ('boolean', 'Example BOOL field'),
        ('datetime', 'Example DATETIME field'),
        ('foreign_key', 'Example ForeignKey field'),
        ('relation_to_example', 'Example Relation field'),
    ]
