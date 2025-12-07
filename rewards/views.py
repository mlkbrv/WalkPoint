# rewards/views.py
from django.utils import timezone
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .models import UserCoupon
from .serializers import UserCouponSerializer
from partners.models import CouponTemplate
from partners.permissions import IsPartner


class BuyCouponView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, template_id):
        user = request.user
        template = get_object_or_404(CouponTemplate, id=template_id)

        if not template.is_active:
            return Response({"error": "Этот купон недоступен."}, status=400)

        if template.quantity is not None and template.quantity <= 0:
            return Response({"error": "Купоны закончились."}, status=400)

        if user.coins < template.cost_coins:
            return Response({"error": "Недостаточно коинов."}, status=400)

        with transaction.atomic():
            user.coins -= template.cost_coins
            user.save()
            if template.quantity is not None:
                template.quantity -= 1
            template.purchased_count += 1
            template.save()
            user_coupon = UserCoupon.objects.create(user=user, template=template)
        return Response(UserCouponSerializer(user_coupon).data, status=status.HTTP_201_CREATED)


class MyCouponsListView(ListAPIView):
    serializer_class = UserCouponSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserCoupon.objects.filter(user=self.request.user).order_by('is_redeemed', '-purchased_at')


class RedeemCouponView(APIView):
    permission_classes = [IsPartner]

    def post(self, request, uuid):
        coupon = get_object_or_404(UserCoupon, redemption_uuid=uuid)

        if coupon.template.partner != request.user.partner:
            return Response({"error": "Вы не можете погасить чужой купон."}, status=403)

        if coupon.is_redeemed:
            return Response({
                "error": "Купон уже использован!",
                "redeemed_at": coupon.redeemed_at
            }, status=400)

        coupon.is_redeemed = True
        coupon.redeemed_at = timezone.now()
        coupon.save()

        return Response({
            "message": "Купон успешно принят!",
            "coupon_title": coupon.template.title,
            "user_email": coupon.user.email
        })