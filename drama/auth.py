from django.conf import settings
import hashlib
from django.contrib.auth import backends, get_user_model
from django.contrib.auth.models import User, check_password
from django.db import models

class EmailBackend(backends.ModelBackend):
    """
    Tries to authenticate the user using the md5 hash of their email as the username
    """
    def authenticate(self, username=None, password=None, **kwargs):
        new_username = hashlib.md5(username.encode('utf-8')).hexdigest()[0:30]
        return super(EmailBackend, self).authenticate(username=new_username, password=password, **kwargs)

class RulePermissionsBackend(backends.ModelBackend):

    def authenticate(self, *args, **kwargs):
        return None

    def has_perm(self, user_obj, perm, obj=None):
        if obj is None:
            return False

        if not isinstance(obj, models.Model):
            return False

        if not user_obj.is_authenticated():
            if settings.ANONYMOUS_USER_ID is None:
                return False
            user_obj = get_user_model().objects.get(pk=settings.ANONYMOUS_USER_ID)

        if not user_obj.is_active:
            return False

        if len(perm.split('.')) > 1:
            app_label, perm = perm.split('.')
            if app_label != obj._meta.app_label:
                raise WrongAppError("Passed perm has app label of '%s' and "
                    "given obj has '%s'" % (app_label, obj._meta.app_label))
        perm_type, obj_type = perm.split('_')
        if perm_type not in ("change", "delete", "approve",):
            return False

        if obj_type != obj.__class__.__name__.lower():
            return False

        if obj_type in ('society', 'venue') and obj.group in user_obj.groups.all():
            return True

        if obj_type in ('show',):
            for soc in obj.societies.all():
                if soc.group in user_obj.groups.all()i and soc.approved():
                    return True
            for performance in obj.performance_set.all():
                if performance.venue.group in user_obj.groups.all():
                    return obj.venue.approved()

        return False
