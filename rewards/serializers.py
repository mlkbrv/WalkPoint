# rewards/serializers.py
from rest_framework import serializers
from .models import UserCoupon
from partners.serializers import CouponTemplateSerializer


class UserCouponSerializer(serializers.ModelSerializer):
    # Вкладываем полную информацию о купоне (название, описание, картинка партнера)
    coupon_details = CouponTemplateSerializer(source='template', read_only=True)

    class Meta:
        model = UserCoupon
        fields = [
            'id',
            'coupon_details',
            'redemption_uuid',
            'qr_code_image',
            'is_redeemed',
            'redeemed_at',
            'purchased_at'
        ]