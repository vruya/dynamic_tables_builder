from django.db import models

APP_LABEL = 'table_manager'

DYNAMIC_TYPES = {
    'string': models.CharField,
    'number': models.FloatField,
    'boolean': models.BooleanField
}

VALID_TYPES = {
    'max_length': int,
    'required': bool,
    'null': bool
}
