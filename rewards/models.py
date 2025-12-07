import uuid
import qrcode
from io import BytesIO
from django.core.files import File
from django.db import models
from django.conf import settings
from partners.models import CouponTemplate


class UserCoupon(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='my_coupons'
    )
    template = models.ForeignKey(
        CouponTemplate,
        on_delete=models.CASCADE,
        related_name='distributed_coupons'
    )

    redemption_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    qr_code_image = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    is_redeemed = models.BooleanField(default=False)
    redeemed_at = models.DateTimeField(null=True, blank=True)
    purchased_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.qr_code_image:
            qr_data = f"{settings.BASE_API_URL}/api/rewards/redeem/{self.redemption_uuid}/"

            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_data)
            qr.make(fit=True)
            img = qr.make_image(fill='black', back_color='white')

            buffer = BytesIO()
            img.save(buffer, format='PNG')
            file_name = f'qr-{self.redemption_uuid}.png'
            self.qr_code_image.save(file_name, File(buffer), save=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Coupon for {self.user} - {self.template.title}"