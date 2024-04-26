import re
import uuid

from django.core.cache import cache
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.db import models, connection
from rest_framework.exceptions import ValidationError

from .constants import APP_LABEL, DYNAMIC_TYPES
from .models import DynamicTable


@receiver(post_save, sender=DynamicTable)
def manage_dynamic_model(sender, instance, created, **kwargs):
    if created:
        create_dynamic_model(instance, True)
    else:
        update_dynamic_model(instance)


@receiver(pre_delete, sender=DynamicTable)
def delete_dynamic_model(sender, instance, **kwargs):
    drop_table(instance.name)


def update_dynamic_model(instance):
    drop_table(instance.name)
    create_dynamic_model(instance, True, uuid.uuid4().hex)


def create_dynamic_model(instance, save=False, new_uuid=None):
    attributes = {'__module__': 'table_manager.models'}
    if not save:
        if model_definition := cache.get(instance.name):
            attributes.update(model_definition['attributes'])
            return type(model_definition['class_name'], (models.Model,), attributes)

    unique_name = f"{instance.name.lower().replace(' ', '_')}_{instance.uuid_hex if not new_uuid else new_uuid}"

    for field_name, field_attr in instance.schema.items():
        try:
            field_class = DYNAMIC_TYPES[field_attr['type']]
        except (TypeError, KeyError):
            raise ValidationError('Schema type is not valid.')

        field_params = field_attr.get('options', {})
        attributes[field_name] = field_class(**field_params)

    NewModel = type(unique_name, (models.Model,), attributes)

    if save:
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(NewModel)
        if new_uuid:
            # Avoid maximum recursion depth
            DynamicTable.objects.filter(id=instance.id).update(uuid_hex=new_uuid)

    model_definition = {
        'class_name': unique_name,
        'attributes': attributes
    }
    cache.set(instance.name, model_definition, timeout=60)

    return NewModel


def drop_table(table_name):
    if re.match(r'^\w+$', table_name):
        if _table_name := fetch_table_name(table_name):
            with connection.cursor() as cursor:
                cursor.execute(f"DROP TABLE IF EXISTS {_table_name[0]};")


def fetch_table_name(table_name):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_name like %s",
            [f'{APP_LABEL}_{table_name}%']
        )
        return cursor.fetchone()
