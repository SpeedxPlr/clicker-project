from django.apps import AppConfig


class ClickerappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'clickerapp'

def ready(self):
    import clickerapp.signals
