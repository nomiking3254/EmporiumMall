from account.models import wallet, withdraw, deposit, income, user_plan, bank_detail, plan, add_bank
from django.core.exceptions import ObjectDoesNotExist

def get_wallet_by_user(user):
        try:
          user_wallet = wallet.objects.get(user=user)
          return user_wallet
        except ObjectDoesNotExist as e:
            return False

def get_user_plans(user):
      all_user_plan = user_plan.objects.filter(user=user)
      return all_user_plan

def get_user_process_plans(user):
      user_in_process_plans = user_plan.objects.filter(user=user, status='In Process')
      return user_in_process_plans

def get_user_Completed_plans(user):
      user_Completed_plans = user_plan.objects.filter(user=user, status='Completed')
      return user_Completed_plans

def update_bank_detail(account_title, account_number, bank_account_id, bank):
        try:
          Bank_detail = bank_detail.objects.get(id=bank_account_id)
          bankname = add_bank.objects.get(id=bank)
          Bank_detail.account_title = account_title
          Bank_detail.account_number = account_number
          Bank_detail.bank_id = bankname
          Bank_detail.save()
          return None
        except ObjectDoesNotExist as e:
          message = 'Internal server error'
          return message
        except Exception as e:
          message = e
          return message
        
def update_plan_detail(plan_name, plan_price,  total_income, duration, lanuch, quantity, id, plan_category, image=None):
      try:
          Plan_detail = plan.objects.get(id=id)
          Plan_detail.name = plan_name
          Plan_detail.total_income = float(total_income)
          Plan_detail.price = float(plan_price)
          Plan_detail.plan_duration = int(duration)
          Plan_detail.is_launch = lanuch
          Plan_detail.plan_category = plan_category
          Plan_detail.quantity_limit = int(quantity)
          if image:
              Plan_detail.image = image
          Plan_detail.save()
          return None
      except ObjectDoesNotExist as e:
          message = e
          return message
      except Exception as e:
          message = e
          return message

def convert_middle_to_asterisk(number):
    number_str = str(number)
    length = len(number_str)
    
    if length <= 2:  # No middle part to replace
        return number
    
    middle_start = length // 2 - 2
    middle_end = middle_start + 4 if length % 2 == 0 else middle_start + 1
    
    modified_str = number_str[:middle_start] + '*' * (4) + number_str[7:]
    modified_number = modified_str
    return modified_number