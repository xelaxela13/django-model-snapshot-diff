# Django model snapshot difference
Make snapshot from Django model with all deep relations and get difference

Example models with other relations like OneToOne, ManyToMany etc.:

```python
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
```
snapshot_fields should be a list of tuples with fields to track, for example:
```python
snapshot_fields = [
    ('model_field_name', 'Verbose name, any text')
]
```
How to use?
```python
example = Example.objects.first()
example.save_snapshot()

example.text = 'new text'
example.save()

diff = example.diff(verbose=True)
assert diff == {'Example TEXT field': {'New Value:': 'new text',
                                        'Old Value': 'text'}}
```
Diff will contain all difference with relations, for full example look for a tests.
# Testing

Tests are found in a simplified Django project in the ```/testapp``` folder. Install the project requirements and do ```./manage.py test``` to run them.

# License

See [License](LICENSE.md).