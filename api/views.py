from django.shortcuts import render
from rest_framework import generics, viewsets
from .models import Item, Bid
from .serializers import ItemSerializer, BidSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from django.utils import timezone
from datetime import timedelta
from rest_framework.exceptions import ValidationError, NotFound
from .tasks import update_item_status
from .filters import ItemFilter
from rest_framework.parsers import MultiPartParser, FormParser

class ItemViewSet(viewsets.ModelViewSet):
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_class = ItemFilter  
    queryset = Item.objects.all()
    parser_classes = [MultiPartParser, FormParser]
    search_fields = ['name', 'description']

    def perform_create(self, serializer):
        item = serializer.save(owner=self.request.user)

        now = timezone.now()

        if item.auction_start_time > now:
            update_item_status.apply_async(
                args=[item.id, 'live'],
                eta=item.auction_start_time
            )
        else:
            update_item_status.delay(item.id, 'live')

        if item.auction_end_time > now:
            update_item_status.apply_async(
                args=[item.id, 'recently_concluded'],
                eta=item.auction_end_time
            )
        else:
            update_item_status.delay(item.id, 'recently_concluded')

        update_item_status.apply_async(
            args=[item.id, 'past'],
            eta=item.auction_end_time + timedelta(days=30)
        )

    def perform_update(self, serializer):
        item = serializer.save()
        now = timezone.now()

        update_item_status.apply_async(
            args=[item.id, 'live'],
            eta=item.auction_start_time if auction_start_time > now else now
        )

        update_item_status.apply_async(
            args=[item.id, 'recent'],
            eta=item.auction_end_time if item.auction_end_time > now else now
        )

        update_item_status.apply_async(
            args=[item.id, 'past'],
            eta=item.auction_end_time + timedelta(days=30)
        )

class MyItemsListView(generics.ListAPIView):
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Item.objects.filter(owner=self.request.user)

class ItemBidsView(generics.ListAPIView):
    serializer_class = BidSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        item_id = self.kwargs.get('item_id')
        try:
            item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            raise NotFound("Item not found")
        
        return Bid.objects.filter(item=item).order_by('-created_at')

class PlaceBidView(generics.CreateAPIView):
    serializer_class = BidSerializer
    permission_classes = [IsAuthenticated]

    def get_item(self):
        try:
            return Item.objects.get(id=self.kwargs['item_id'])
        except Item.DoesNotExist:
            raise NotFound("Item not found")

    def perform_create(self, serializer):
        item = self.get_item()

        if item.owner == self.request.user:
            raise ValidationError("You cannot bid on your own item")

        if timezone.now() > item.auction_end_time:
            raise ValidationError("Auction has ended")

        amount = self.request.data.get('amount')
        if not amount:
            raise ValidationError("Bid amount is required")

        amount = float(amount)

        if item.highest_bid and amount <= float(item.highest_bid.amount):
            raise ValidationError("Bid must be higher than current highest bid")

        if not item.highest_bid and amount <= float(item.price):
            raise ValidationError("Bid must be higher than starting price")


        bid = serializer.save(item=item, user=self.request.user)
        item.highest_bid = bid
        item.save()

