from django.urls import path
from . import views
urlpatterns = [
    path('items/', views.ItemListView.as_view(), name='item-list'),
    path('items/create', views.ItemCreateView.as_view(), name='item-create'),
    path('my-items/', views.MyItemsListView.as_view(), name='my-items-list'),
    path('items/<int:item_id>/bid/', views.PlaceBidView.as_view(), name='item-bid'),
]
