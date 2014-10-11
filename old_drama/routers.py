class MigrationRouter(object):
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'old_drama':
            return 'old'
        return None

    
    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'old_drama':
            return 'old'
        return None
