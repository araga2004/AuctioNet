from rest_framework import serializers
from .models import Item, CustomUser, Bid

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email']

class BidSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    class Meta:
        model = Bid
        fields = ['item', 'user', 'amount', 'created_at']
        read_only_fields = ['item', 'user']

class ItemSerializer(serializers.ModelSerializer):
    owner = CustomUserSerializer(read_only=True)
    highest_bid = BidSerializer(read_only=True)
    class Meta:
        model = Item
        fields = ['id', 'name', 'description', 'price', 'created_at', 'updated_at', 'owner', 'highest_bid']
        read_only_fields = ['created_at', 'updated_at', 'owner', 'highest_bid']

