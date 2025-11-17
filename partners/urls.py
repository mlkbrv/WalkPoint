from django.urls import path
from .views import (
    CouponMarketplaceView,
    PartnerListView,
    PartnerCouponManagementView,
    PartnerCouponDetailView,
    PartnerDashboardStatsView
)

urlpatterns = [
    path('marketplace/', CouponMarketplaceView.as_view(), name='marketplace'),
    path('brands/', PartnerListView.as_view(), name='brands_list'),

    path('dashboard/', PartnerDashboardStatsView.as_view(), name='partner_dashboard'),
    path('my-coupons/', PartnerCouponManagementView.as_view(), name='partner_coupons_list_create'),
    path('my-coupons/<int:pk>/', PartnerCouponDetailView.as_view(), name='partner_coupon_detail'),
]