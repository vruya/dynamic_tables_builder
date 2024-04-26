import uuid

from django.db import models


class DynamicTable(models.Model):
    name = models.CharField(max_length=255, unique=True)
    uuid_hex = models.CharField(max_length=32, unique=True)
    schema = models.JSONField()
    '''
    type: DYNAMIC_TYPES
    options: {
        django field params
    }
    '''

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk:
            self.uuid_hex = uuid.uuid4().hex
        super().save(*args, **kwargs)
