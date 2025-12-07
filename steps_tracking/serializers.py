from rest_framework import serializers
from .models import DailyActivity, CoinTransaction


class DailyActivitySerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = DailyActivity
        fields = ['id',
                  'user',
                  'date',
                  'duration',
                  'steps',
                  'distance_km',
                  'calories_burned',
                  'source_app'
                  ]
        read_only_fields = ['user']

        # Убрали валидатор, так как unique_together уже определен в модели
        # и Django автоматически проверяет уникальность на уровне БД


class CoinTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoinTransaction
        fields = ['amount', 'transaction_type', 'reason', 'created_at']
