from django.core.exceptions import ValidationError
from .models import UserPromotion


def redeem_promotion(user, promotion):
    if user.available_steps < promotion.required_steps:
        raise ValidationError("Not enough steps to get the share.")

    count = UserPromotion.objects.filter(user=user, promotion=promotion).count()
    if count >= promotion.max_redemptions_per_user:
        raise ValidationError("You have already used this promotion the maximum number of times allowed..")

    user.available_steps -= promotion.required_steps
    user.save()

    return UserPromotion.objects.create(user=user, promotion=promotion)
