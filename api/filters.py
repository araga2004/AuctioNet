import django_filters
from .models import Item

class ItemFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr='lte')
    status = django_filters.CharFilter(field_name="status", lookup_expr='iexact')

    class Meta:
        model = Item
        fields = ['min_price', 'max_price', 'status']
