from django.urls import path
from .views import (
    PartnerList,
    PromotionList,
    AllPromotionList,
    PromotionDetail,
    PromotionPurchaseView,
    UserRedemptionsView
)

urlpatterns = [
    path('partners/', PartnerList.as_view(), name='partner-list'),
    path('promotions/', PromotionList.as_view(), name='promotion-list'),
    path('promotions/all/', AllPromotionList.as_view(), name='all-promotion-list'),
    path('promotions/<uuid:pk>/', PromotionDetail.as_view(), name='promotion-detail'),
    path('promotions/purchase/', PromotionPurchaseView.as_view(), name='promotion-purchase'),
    path('promotions/my-redemptions/', UserRedemptionsView.as_view(), name='user-redemptions'),
]
