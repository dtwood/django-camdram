from django.apps import AppConfig
import simple_history
from django.contrib.auth.models import User


class DramaConfig(AppConfig):
    name = 'drama'
    verbose_name = 'Camdram main app'
    def ready(self):
        import drama.signals
        simple_history.register(User)
        
