from django.urls import path
from .views import BuyCouponView, MyCouponsListView, RedeemCouponView

urlpatterns = [
    path('buy/<int:template_id>/', BuyCouponView.as_view(), name='buy_coupon'),

    path('my-coupons/', MyCouponsListView.as_view(), name='my_coupons'),

    path('redeem/<uuid:uuid>/', RedeemCouponView.as_view(), name='redeem_coupon'),
]