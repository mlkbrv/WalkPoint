from django.contrib import admin
from .models import Partner,Promotion,UserPromotion,PartnerAccount

admin.site.register(Partner)
admin.site.register(Promotion)
admin.site.register(UserPromotion)
admin.site.register(PartnerAccount)