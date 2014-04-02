from django.conf import settings
import hashlib
from django.contrib.auth import backends, get_user_model
from django.contrib.auth.models import User, check_password

class EmailBackend(backends.ModelBackend):
    """
    Tries to authenticate the user using the md5 hash of their email as the username
    """
    def authenticate(self, username=None, password=None, **kwargs):
        new_username = hashlib.md5(username.encode('utf-8')).hexdigest()[0:30]
        return super(EmailBackend, self).authenticate(username=new_username, password=password, **kwargs)
