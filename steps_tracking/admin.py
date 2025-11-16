from django.contrib import admin
from .models import CoinTransaction,DailyActivity

admin.site.register(CoinTransaction)
admin.site.register(DailyActivity)