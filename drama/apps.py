from django.apps import AppConfig


class DramaConfig(AppConfig):
    name = 'drama'
    verbose_name = 'Camdram main app'
    def ready(self):
        import drama.signals
        
