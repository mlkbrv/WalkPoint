from rest_framework import serializers
from .models import Partner, CouponCategory, CouponTemplate

class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partner
        fields = [
            'id',
            'name',
            'description',
            'logo',
            'website',
        ]

class CouponCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CouponCategory
        fields = [
            'id',
            'name',
            'slug',
            'icon'
        ]

class CouponTemplateSerializer(serializers.ModelSerializer):
    partner_details = PartnerSerializer(source='partner',read_only=True)
    category_details = CouponCategorySerializer(source="category",read_only=True)

    category = serializers.PrimaryKeyRelatedField(queryset=CouponCategory.objects.all(),write_only=True)

    class Meta:
        model = CouponTemplate
        fields = [
            'id',
            'partner_details',
            'category_details',
            'category',
            'title',
            'description',
            'cost_coins',
            'validity_days',
            'quantity',
            'purchased_count',
            'is_active',
            'created_at'
        ]
        read_only_fields = ['partner_details', 'purchased_count', 'created_at']