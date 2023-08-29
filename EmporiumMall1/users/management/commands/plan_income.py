from django.core.exceptions import ObjectDoesNotExist
from account.models import wallet, income, user_plan
import threading
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand
from django.core.management import call_command


def plan_income_task():
      current_time = datetime.now().time()
      # current_hour = current_time.hour
   #  if current_hour >= 2 and current_hour < 3:
      user_plans = user_plan.objects.filter(status='In Process')
      for i in user_plans:
            plan_start_time = i.started_at
            plan_end_time = i.completed_at
            time_diff = timezone.now() - plan_start_time
            if time_diff > timedelta(minutes=59):
               try:
                  latest_income= income.objects.filter(user=i.user, user_plan=user_plan.objects.get(id=i.id)).latest('income_at')
                  time_diff = timezone.now() - latest_income.income_at
                  if time_diff > timedelta(minutes=59):
                     income.create_user_income(i.plan.hourly_income, i.user, "My Investment Income", user_plan=user_plan.objects.get(id=i.id))
               except ObjectDoesNotExist as e:
                  latest_income = False
                  income.create_user_income(i.plan.hourly_income, i.user, "My Investment Income", user_plan=user_plan.objects.get(id=i.id))

            if plan_end_time < timezone.now():
               user_plans_complete = user_plan.objects.get(id=i.id)
               user_plans_complete.status = "Completed"
               user_plans_complete.save()
      threading.Timer(30 * 60, plan_income_task).start()
   #  else:
   #       # Schedule the next execution after 10 minutes
   #      threading.Timer(60 * 60, plan_income_task).start()

class Command(BaseCommand):
    help = 'Starts the auto add task'

    def handle(self, *args, **options):
        # Start the periodic task
        plan_income_task()