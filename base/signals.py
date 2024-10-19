from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Room

@receiver(post_save, sender=Room)
@receiver(post_delete, sender=Room)
def clear_cache(sender, **kwargs):
    cache.clear()