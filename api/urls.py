from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter

urlpatterns = [
    path('my-items/', views.MyItemsListView.as_view(), name='my-items-list'),
    path('items/<int:item_id>/bid/', views.PlaceBidView.as_view(), name='item-bid'),
    path('items/<int:item_id>/bids/', views.ItemBidsView.as_view(), name='item-bids'),
]

router = DefaultRouter()
router.register(r'items', views.ItemViewSet, basename='item')

urlpatterns += router.urls