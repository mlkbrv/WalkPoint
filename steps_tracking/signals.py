# steps_tracking/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import DailyActivity, CoinTransaction

User = get_user_model()

MIN_STEPS_THRESHOLD = 5000
STEP_INCREMENT = 1000
COIN_PER_INCREMENT = 1


def calculate_daily_reward(steps):
    if steps < MIN_STEPS_THRESHOLD:
        return 0

    return int(steps / STEP_INCREMENT)


@receiver(post_save, sender=DailyActivity)
def handle_daily_reward(sender, instance, **kwargs):
    user = instance.user
    date = instance.date

    new_reward = calculate_daily_reward(instance.steps_count)

    reason_string = f"Daily Steps Reward ({date})"

    try:
        existing_txn = CoinTransaction.objects.get(
            user=user,
            reason=reason_string,
            transaction_type=CoinTransaction.TransactionType.EARNED
        )
        old_reward = existing_txn.amount
    except CoinTransaction.DoesNotExist:
        existing_txn = None
        old_reward = 0

    difference = new_reward - old_reward

    if difference == 0:
        return

    user.coins += difference
    user.save(update_fields=['coins'])

    if new_reward == 0:
        if existing_txn:
            existing_txn.delete()
    elif existing_txn:
        existing_txn.amount = new_reward
        existing_txn.save(update_fields=['amount'])
    else:
        CoinTransaction.objects.create(
            user=user,
            amount=new_reward,
            transaction_type=CoinTransaction.TransactionType.EARNED,
            reason=reason_string
        )
