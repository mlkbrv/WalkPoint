from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from users.models import User, DailyStep


class Command(BaseCommand):
    help = 'Transfer daily steps to user accounts for the previous day'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Specific date to process (YYYY-MM-DD). Defaults to yesterday.',
        )

    def handle(self, *args, **options):
        # Determine which date to process
        if options['date']:
            try:
                target_date = date.fromisoformat(options['date'])
            except ValueError:
                self.stdout.write(
                    self.style.ERROR('Invalid date format. Use YYYY-MM-DD')
                )
                return
        else:
            # Default to yesterday
            target_date = date.today() - timedelta(days=1)

        self.stdout.write(f'Processing daily steps for {target_date}...')

        # Get all users who have daily steps for this date
        daily_steps = DailyStep.objects.filter(date=target_date, steps__gt=0)
        
        if not daily_steps.exists():
            self.stdout.write(
                self.style.WARNING(f'No daily steps found for {target_date}')
            )
            return

        transferred_count = 0
        total_steps_transferred = 0

        for daily_step in daily_steps:
            user = daily_step.user
            steps_transferred = user.transfer_daily_steps(target_date)
            
            if steps_transferred > 0:
                transferred_count += 1
                total_steps_transferred += steps_transferred
                self.stdout.write(
                    f'Transferred {steps_transferred} steps to {user.email}'
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully transferred steps for {transferred_count} users. '
                f'Total steps transferred: {total_steps_transferred}'
            )
        )
