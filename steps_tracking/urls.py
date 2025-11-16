from django.urls import path
from .views import DailyActivityListCreateView, CoinTransactionListView

urlpatterns = [
    path('activity/', DailyActivityListCreateView.as_view(), name='daily_activity_list_create'),
    path('transactions/', CoinTransactionListView.as_view(), name='coin_transaction_list'),
]