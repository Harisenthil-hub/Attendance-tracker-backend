from django.db.models import F
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import AppUser,SystemStats

@receiver(post_save,sender=AppUser)
def stats_on_user_create(sender,instance,created, **kwargs):
    if created:
        stats, _ = SystemStats.objects.get_or_create(id=1)
        stats.total_users = F('total_users')+1
        if instance.status == 'active':
            stats.total_active_users = F('total_active_users')+1
        if instance.role == 'admin':
            stats.total_admins = F('total_admins')+1
        stats.last_updated_at = timezone.now()
        stats.save()
            

@receiver(pre_save,sender=AppUser)
def stats_on_user_update(sender,instance,**kwargs):

    if not instance.pk:
        return

    old = AppUser.objects.get(pk=instance.pk)
    stats, _ = SystemStats.objects.get_or_create(id=1)


    if old.status != instance.status:

        if old.status == 'active' and stats.total_active_users > 0:
            stats.total_active_users = F('total_active_users')-1
        if old.status == 'suspended' and stats.total_suspended > 0:
            stats.total_suspended = F('total_suspended')-1
        if old.status == 'terminated' and stats.total_terminated > 0:
            stats.total_terminated = F('total_terminated')-1


        if instance.status == 'active':
            stats.total_active_users = F('total_active_users')+1
        if instance.status == 'suspended':
            stats.total_suspended = F('total_suspended')+1
        if instance.status == 'terminated':
            stats.total_terminated = F('total_terminated')+1


    if old.role != instance.role:
        if old.role == 'admin' and stats.total_admins > 0:
            stats.total_admins = F('total_admins')-1
        if instance.role == 'admin':
            stats.total_admins = F('total_admins')+1

    stats.last_updated_at =  timezone.now()
    stats.save()
