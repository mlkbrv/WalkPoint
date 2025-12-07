from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import serializers
from django.db import IntegrityError
from .models import DailyActivity, CoinTransaction
from .serializers import DailyActivitySerializer, CoinTransactionSerializer

class DailyActivityListCreateView(generics.ListCreateAPIView):
    serializer_class = DailyActivitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DailyActivity.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError as e:
            if 'unique' in str(e).lower():
                return Response(
                    {'date': ['An activity record for this date already exists.']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            raise

class CoinTransactionListView(generics.ListAPIView):
    serializer_class = CoinTransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CoinTransaction.objects.filter(user=self.request.user)