from django.shortcuts import render
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.views import APIView
from django.db import transaction
from .serializers import *
from .models import *
from .permissions import IsPartner


class PartnerList(generics.ListCreateAPIView):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer
    permission_classes = [IsAdminUser]


class PromotionList(generics.ListCreateAPIView):
    serializer_class = PromotionSerializer
    permission_classes = [IsAuthenticated, IsPartner]

    def get_queryset(self):
        return Promotion.objects.filter(partner=self.request.user.partner_account.partner)

    def perform_create(self, serializer):
        serializer.save(partner=self.request.user.partner_account.partner)


class AllPromotionList(generics.ListAPIView):
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Promotion.objects.filter(is_active=True)


class PromotionDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer

    def get_permissions(self):
        if self.request.method in ("PUT", "PATCH", "DELETE"):
            return [IsAuthenticated(), IsPartner()]
        return [IsAuthenticated]


class PromotionPurchaseView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = PromotionPurchaseSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        promotion_uuid = serializer.validated_data['promotion_uuid']
        user = request.user
        
        try:
            with transaction.atomic():
                promotion = Promotion.objects.get(uuid=promotion_uuid, is_active=True)

                if user.available_steps < promotion.required_steps:
                    return Response(
                        {
                            'error': 'Insufficient steps',
                            'required_steps': promotion.required_steps,
                            'available_steps': user.available_steps
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                redemption_count = UserPromotion.objects.filter(
                    user=user, 
                    promotion=promotion
                ).count()
                
                if redemption_count >= promotion.max_redemptions_per_user:
                    return Response(
                        {
                            'error': 'Maximum redemptions reached',
                            'max_redemptions': promotion.max_redemptions_per_user,
                            'current_redemptions': redemption_count
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                user_promotion = UserPromotion.objects.create(
                    user=user,
                    promotion=promotion
                )

                user.available_steps -= promotion.required_steps
                user.save(update_fields=['available_steps'])


                return Response(
                    {
                        'message': 'Promotion redeemed successfully',
                        'promotion': PromotionSerializer(promotion).data,
                        'redeemed_at': user_promotion.redeemed_at,
                        'remaining_steps': user.available_steps
                    },
                    status=status.HTTP_201_CREATED
                )
                
        except Promotion.DoesNotExist:
            return Response(
                {'error': 'Promotion not found or inactive'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': 'An error occurred during redemption'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserRedemptionsView(generics.ListAPIView):
    serializer_class = UserPromotionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserPromotion.objects.filter(user=self.request.user).order_by('-redeemed_at')
