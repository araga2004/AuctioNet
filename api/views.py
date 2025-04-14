from django.shortcuts import render
from rest_framework import generics
from .models import Item
from .serializers import ItemSerializer, BidSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from rest_framework.exceptions import ValidationError

class ItemListView(generics.ListAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [AllowAny]

class ItemCreateView(generics.CreateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated] 

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class MyItemsListView(generics.ListAPIView):
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Item.objects.filter(owner=self.request.user)


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

