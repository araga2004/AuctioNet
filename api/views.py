from django.shortcuts import render
from rest_framework import generics, viewsets
from .models import Item, Bid
from .serializers import ItemSerializer, BidSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from django.utils import timezone
from datetime import timedelta
from rest_framework.exceptions import ValidationError, NotFound

class ItemViewSet(viewsets.ModelViewSet):
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    def get_queryset(self):
        status = self.request.query_params.get('status')
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)

        if status == 'upcoming':
            return Item.objects.filter(auction_start_time__gt=now)
        elif status == 'live':
            return Item.objects.filter(auction_start_time__lte=now, auction_end_time__gt=now)
        elif status == 'recent':
            return Item.objects.filter(auction_end_time__lte=now, auction_end_time__gte=thirty_days_ago)
        elif status == 'past':
            return Item.objects.filter(auction_end_time__lt=thirty_days_ago)
        elif status in [None, 'all']:
            return Item.objects.all()
        else:
            raise ValidationError('Invalid status value')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

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

