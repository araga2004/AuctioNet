from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Item

@shared_task
def update_item_status(item_id, new_status):
    try:
        item = Item.objects.get(id=item_id)
        now = timezone.now()

        if new_status == 'live' and item.auction_start_time <= now < item.auction_end_time:
            item.status = 'live'
            item.save(update_fields=['status'])
        elif new_status == 'recent' and item.auction_end_time <= now < item.auction_end_time + timedelta(days=30):
            item.status = 'recent'
            item.save(update_fields=['status'])
        elif new_status == 'past' and now >= item.auction_end_time + timedelta(days=30):
            item.status = 'past'
            item.save(update_fields=['status'])

    except Item.DoesNotExist:
        pass
