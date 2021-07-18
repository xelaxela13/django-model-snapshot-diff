import re
from deepdiff import DeepDiff
from django.core.exceptions import FieldDoesNotExist
from django.db.models.fields.files import FieldFile
from django.db.models import JSONField
from django.db.models.manager import BaseManager


class SnapshotMixin:
    db_field_name = 'snapshot'
    snapshot_fields = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__results = dict()

    def __get_snapshot_fields(self):
        return getattr(self, 'snapshot_fields', [])

    def make_snapshot(self, rel=False):
        results = dict() if rel else self.__results
        for field, verbose in self.__get_snapshot_fields():
            value = getattr(self, field)
            # ManyToMany field
            if isinstance(value, BaseManager):
                result = [item.make_snapshot(True) for item in value.all()]
                results[verbose] = result
            # ForeignKey, OneToOne field
            elif isinstance(value, SnapshotMixin):
                results[verbose] = value.make_snapshot(True)
            elif isinstance(value, FieldFile):
                try:
                    file_name = value.name
                except ValueError:
                    file_name = None
                if file_name:
                    results[verbose] = file_name.split('/')[-1]
                else:
                    results[verbose] = 'No file'
            else:
                if len(self.__get_snapshot_fields()) == 1 and field == 'id':
                    return str(value)
                results[verbose] = str(value)
        return results

    def save_snapshot(self, snapshot=None):
        try:
            field = self._meta.get_field(self.db_field_name)
            if not isinstance(field, JSONField):
                raise FieldDoesNotExist()
        except FieldDoesNotExist:
            pass
        else:
            setattr(self, self.db_field_name, snapshot or self.make_snapshot())
            self.save(update_fields=(self.db_field_name, ))

    def diff(self, first=None, second=None, verbose=False) -> dict:
        if not first:
            try:
                first = getattr(self, self.db_field_name)
            except AttributeError:
                return {}
        second = second or self.make_snapshot()
        diff = DeepDiff(first, second, verbose_level=2,
                        ignore_order=True).to_dict()
        return self.__verbose_diff(diff) if verbose else diff

    def __verbose_diff(self, diff: dict) -> dict:
        result = dict()
        for key, value in diff.get('values_changed', {}).items():
            verbose_keys = re.findall(r"\['(.*?)\']", key)
            if len(verbose_keys) == 1:
                result[verbose_keys[0]] = {'New Value:': value['new_value'],
                                           'Old Value': value['old_value']}
            elif len(verbose_keys) > 1:
                result[' -> '.join(verbose_keys)] = {
                    'New Value:': value['new_value'],
                    'Old Value': value['old_value']
                }

        for t, k in (('Removed', 'iterable_item_removed'),
                     ('Added', 'iterable_item_added')):
            items_name = []
            for key, value in diff.get(k, {}).items():
                verbose_keys = re.findall(r"\['(.*?)\']", key)
                if len(verbose_keys) >= 1:
                    items_name.append(', '.join(value.values()))
                result[
                    f"{t} data: {' -> '.join(verbose_keys)}"
                ] = ', '.join(items_name)
        return result
