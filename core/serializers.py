from rest_framework import serializers
from .models import Partner,Promotion,UserPromotion
from users.serializers import UserSerializer

class PartnerSerializer(serializers.ModelSerializer):
    icon = serializers.ImageField(use_url=True)

    class Meta:
        model = Partner
        fields = [
            'name',
            'description',
            'icon'
        ]

class PromotionSerializer(serializers.ModelSerializer):
    partner = PartnerSerializer(read_only=True)
    class Meta:
        model = Promotion
        fields = [
            'uuid',
            'partner',
            'title',
            'description',
            'required_steps',
            'is_active',
            'max_redemptions_per_user'
        ]

class UserPromotionSerializer(serializers.ModelSerializer):
    promotion = PromotionSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    class Meta:
        model = UserPromotion
        fields = [
            'user',
            'promotion',
            'redeemed_at'
        ]
