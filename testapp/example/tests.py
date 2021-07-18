import datetime

from django.test import TestCase
from testapp.example.models import ManyToMany, Relation, ForeignKey, \
    ForeignKeyDeeper, Example


class ModelSnapshotMixinTestCase(TestCase):
    def setUp(self):
        foreign_key_deeper = ForeignKeyDeeper.objects.create(name='name')
        for i in range(5):
            foreign_key_deeper.many_to_many.add(
                ManyToMany.objects.create(description=f'description_{i}')
            )
        foreign_key = ForeignKey.objects \
            .create(title='title',
                    foreign_key_deeper=foreign_key_deeper)
        example = Example.objects.create(text='text',
                                         boolean=False,
                                         datetime=datetime.datetime.now(),
                                         foreign_key=foreign_key)
        Relation.objects.create(choice=1, rel_to_example=example)

    def test_snapshot_model(self):
        example = Example.objects.first()
        self.assertIsNone(example.snapshot)

        example.save_snapshot()
        example.refresh_from_db()
        shot = {'Example TEXT field': 'text',
                'Example BOOL field': 'False',
                'Example DATETIME field': example.snapshot[
                    'Example DATETIME field'
                ],
                'Example ForeignKey field': {
                    'ForeignKey TITLE field': 'title',
                    'ForeignKey DEEPER field': {
                        'ForeignKeyDeeper NAME field': 'name',
                        'ForeignKeyDeeper MANYTOMANY field': [
                            {'ManyToMany DESCRIPTION field': 'description_0'},
                            {'ManyToMany DESCRIPTION field': 'description_1'},
                            {'ManyToMany DESCRIPTION field': 'description_2'},
                            {'ManyToMany DESCRIPTION field': 'description_3'},
                            {'ManyToMany DESCRIPTION field': 'description_4'}
                        ]}},
                'Example Relation field': [{'Relation CHOICE field': '1'}]}
        self.assertEqual(example.snapshot, shot)
        self.assertEqual(example.diff(), {})

        example.text = 'new text'
        example.boolean = True
        old_datetime = str(example.datetime)
        example.datetime = datetime.datetime.now()
        example.save()

        relation = Relation.objects.first()
        relation.choice = 2
        relation.save()

        foreign_key = ForeignKey.objects.first()
        foreign_key.title = 'new title'
        foreign_key.save()

        foreign_key_deeper = ForeignKeyDeeper.objects.first()
        foreign_key_deeper.name = 'new name'
        foreign_key_deeper.save()

        many_to_many = ManyToMany.objects.get(id=1)
        many_to_many.description = 'new description'
        many_to_many.save()

        foreign_key_deeper.many_to_many.remove(
            foreign_key_deeper.many_to_many.get(id=2)
        )
        foreign_key_deeper.many_to_many.remove(
            foreign_key_deeper.many_to_many.get(id=3)
        )
        foreign_key_deeper.many_to_many.add(
            ManyToMany.objects.create(description='newest description')
        )

        example.refresh_from_db()
        diff = example.diff(verbose=True)

        _diff = {'Example TEXT field': {'New Value:': example.text,
                                        'Old Value': 'text'},
                 'Example BOOL field': {'New Value:': str(example.boolean),
                                        'Old Value': 'False'},
                 'Example DATETIME field': {
                     'New Value:': str(example.datetime),
                     'Old Value': old_datetime},
                 'Example ForeignKey field -> ForeignKey TITLE field': {
                     'New Value:': foreign_key.title,
                     'Old Value': 'title'},
                 'Example ForeignKey field -> ForeignKey DEEPER field -> '
                 'ForeignKeyDeeper NAME field': {
                     'New Value:': foreign_key_deeper.name,
                     'Old Value': 'name'},
                 'Example ForeignKey field -> ForeignKey DEEPER field -> '
                 'ForeignKeyDeeper MANYTOMANY field -> '
                 'ManyToMany DESCRIPTION field': {
                     'New Value:': many_to_many.description,
                     'Old Value': 'description_2'},
                 'Example Relation field -> Relation CHOICE field': {
                     'New Value:': str(relation.choice), 'Old Value': '1'},
                 'Removed data: Example ForeignKey field -> '
                 'ForeignKey DEEPER field -> ForeignKeyDeeper '
                 'MANYTOMANY field': 'description_0, description_1',
                 'Added data: Example ForeignKey field -> '
                 'ForeignKey DEEPER field -> ForeignKeyDeeper '
                 'MANYTOMANY field': 'newest description'}
        self.assertEqual(diff, _diff)
