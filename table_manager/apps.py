from django.apps import AppConfig


class TableManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'table_manager'

    def ready(self):
        from . import signals
