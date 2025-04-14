from django.utils import timezone
import datetime

def default_auction_end_time():
    return timezone.now() + datetime.timedelta(days=7)