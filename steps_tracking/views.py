from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import DailyActivity, CoinTransaction
from .serializers import DailyActivitySerializer, CoinTransactionSerializer

class DailyActivityListCreateView(generics.ListCreateAPIView):
    serializer_class = DailyActivitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DailyActivity.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CoinTransactionListView(generics.ListAPIView):
    serializer_class = CoinTransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CoinTransaction.objects.filter(user=self.request.user)