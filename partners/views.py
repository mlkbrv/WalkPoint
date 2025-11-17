from rest_framework import generics, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Sum

from .models import CouponTemplate, Partner, CouponCategory
from .serializers import CouponTemplateSerializer, PartnerSerializer, CouponCategorySerializer
from .permissions import IsPartner, IsOwnerOfCoupon

class CouponMarketplaceView(generics.ListAPIView):
    queryset = CouponTemplate.objects.filter(is_active=True,partner__is_active=True)
    serializer_class = CouponTemplateSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('title','description','partner__name')
    ordering_fields = ['cost_coins','created_at']

class PartnerListView(generics.ListAPIView):
    queryset = Partner.objects.filter(is_active=True)
    serializer_class = PartnerSerializer
    permission_classes = [IsAuthenticated]

class PartnerCouponManagementView(generics.ListCreateAPIView):
    serializer_class = CouponTemplateSerializer
    permission_classes = [IsPartner]

    def get_queryset(self):
        return CouponTemplate.objects.filter(partner=self.request.user.partner)

    def perform_create(self, serializer):
        serializer.save(partner=self.request.user.partner)

class PartnerCouponDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CouponTemplate.objects.all()
    serializer_class = CouponTemplateSerializer
    permission_classes = [IsPartner, IsOwnerOfCoupon]

class PartnerDashboardStatsView(APIView):
    permission_classes = [IsPartner]

    def get(self, request):
        partners = self.request.user.partner
        my_coupons = CouponTemplate.objects.filter(partner=partners)

        total_active_coupons = CouponTemplate.objects.filter(is_active=True).count()
        total_sold = my_coupons.aggregate(Sum('purchased_count'))['purchased_count__sum'] or 0
        revernue_coins = sum(c.cost_coins * c.purchased_count for c in my_coupons)

        return Response({
            'partner_name': partners.name,
            "stats":{
                "total_active_coupons": total_active_coupons,
                "total_sold": total_sold,
                "revernue_coins": revernue_coins,
            }
        })