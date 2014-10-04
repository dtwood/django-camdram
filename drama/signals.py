from django.dispatch import receiver
from registration import signals
from drama import models
from guardian.shortcuts import assign_perm


@receiver(signals.user_activated)
def pending_admins(sender, **kwargs):
    email = kwargs['user'].email
    user = kwargs['user']
    for pa in models.PendingAdmin.objects.filter(email=email):
        assign_perm('drama.change_show', user, pa.show)
        pa.delete()
    for pg in models.PendingGroupMember.objects.filter(email=email):
        pg.group.user_set.add(user)
        pg.delete()
        
@receiver(signals.user_activated)
def default_permissions(sender, user, **kwargs):
    user.user_permissions.add('drama.add_show',',drama.add_venue','drama.add_society','drama.add_person','drama.add_role')
