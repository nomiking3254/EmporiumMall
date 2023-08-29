from datetime import timedelta
import os
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from account.models import wallet, plan, deposit, withdraw, income, bank_detail, user_plan, add_bank
from auths.helper import UserLoginRequiredMixin as LoginRequiredMixin
from auths.models import User
from users.models import notification
from admin_panel.models import company_profile, whatsapp_group_link
from auths.helper import change_password_validate
from account import helper
from account.helper import convert_middle_to_asterisk
import random
from django.db.models import Q, Sum, Min
from django.utils import timezone
from users.management.commands.plan_income import plan_income_task


class plan_income(View):
     def get(self, request):
        plan_income_task()
        return redirect('/') 
     
# Create your views here.
class Home(LoginRequiredMixin, View):
    login_url='/Auth/'

    def get(self, request):
      plan_buy_count = []
      user_wallet = wallet.objects.get(user=request.user.id)
      User_plans = user_plan.objects.filter(user__id=request.user.id).order_by("plan__price")
      withdraws = withdraw.objects.filter(status='Withdraw Success').order_by('-id')
      deposts = deposit.objects.filter(status='Deposit Success').order_by('-deposit_request_at')

      plans = plan.objects.all().order_by('price')
      withdraw_notification_list = []
      deposit_notification_list = []

      for j in withdraws:
          converted_str = convert_middle_to_asterisk(int(j.user.phone_number))
          withdraw_notification_list.append(converted_str)
      for d in deposts:
          converted_str = convert_middle_to_asterisk(int(d.user.phone_number))
          deposit_notification_list.append(converted_str)
      for i in plans:
         count = 0
         for j in User_plans:
            if i.id == j.plan.id:
               count = count + 1
         plan_buy_count.append(count)

      Data = { 
              'user_wallet': user_wallet, 
              'all_plans':plans,
              "plan_buy_count": plan_buy_count, 
              'withdraws': withdraws,
              'deposts' : deposts,
              'withdraw_notification_list' : withdraw_notification_list,
              'deposit_notification_list' : deposit_notification_list,
              }
      if company_profile.objects.all():
         Company_profile = company_profile.objects.all().first()
         Data['Company_profile'] = Company_profile
      if whatsapp_group_link.objects.all():
         Whatsapp_link = whatsapp_group_link.objects.all().first()
         Data['Whatsapp_link'] = Whatsapp_link
      return render(request, 'home.html', Data)
   
class Recharge(LoginRequiredMixin, View):
    login_url='/Auth/'

    def get(self, request):
      user_wallet = wallet.objects.get(user=request.user.id)
      Data = { 
               'user_wallet': user_wallet,
             }
      if company_profile.objects.all():
         Company_profile = company_profile.objects.all().first()
         Data['Company_profile'] = Company_profile
      return render(request, 'recharge.html', Data)
    
    def post(self, request, *args):
       try:
          data = request.POST
          recharge_amount = data.get('recharge_amount', None)
          image = request.FILES.getlist('images', None)
          user_wallet = wallet.objects.get(user=request.user.id)
          five_second_ago = timezone.now() -  timedelta(seconds=5)
          if image:
           if deposit.objects.filter(user=request.user, deposit_request_at__gte=five_second_ago):
               pass
           else:
              deposit.create_deposit_request(recharge_amount, request.user.id, image)
              messages.success(request, 'Your Deposit Request is submit successfully.Amount will be added within 30 mins')
          elif recharge_amount:
              account_list = []
              admin = User.objects.filter(is_superuser=True).first()
              admin_accounts = bank_detail.objects.filter(user__username=admin)
              if admin_accounts:
                for i in admin_accounts:
                  account_list.append(i.id)
                random.shuffle(account_list)
                random_account = random.choice(account_list)
                account_details = bank_detail.objects.get(id=random_account)
                Data = {
                        'recharge_amount':recharge_amount, 
                        'account_details': account_details, 
                        'user_wallet': user_wallet,
                        }
                if company_profile.objects.all():
                     Company_profile = company_profile.objects.all().first()
                     Data['Company_profile'] = Company_profile
                return render(request, 'account_details.html', Data)
              else:
                 messages.error(request, "Active deposit account is not found")
       except ObjectDoesNotExist as e:
          return redirect('/recharge/')
       return redirect('/recharge/')
    
class Bank_amount_setting(LoginRequiredMixin, View):
    login_url='/Auth/'

    def get(self, request):
      user_wallet = wallet.objects.get(user=request.user.id)
      bank_names = add_bank.objects.all()
      Data = {'user_wallet': user_wallet,
               'bank_names' :bank_names,
               }
      if bank_detail.objects.filter(user__id=request.user.id):
         user_bank_account = bank_detail.objects.get(user__id=request.user.id)
         Data = { 
                 'user_wallet': user_wallet, 
                 'bank_names' :bank_names,
                 'user_bank_account': user_bank_account,
                  }
      if company_profile.objects.all():
         Company_profile = company_profile.objects.all().first()
         Data['Company_profile'] = Company_profile
      return render(request, 'bank_account_setting.html', Data)
    
    def post(self, request, *args):
       data = request.POST
       account_name = data.get('account_name')
       account_number = data.get('account_number')
       bank = data.get('bank')
       bank_account_id = data.get('id', None)
       action = ''

       if bank_account_id == None:
          message = bank_detail.create_bank_detail(account_name, account_number, request.user, bank)
          action = "added"
       else:
          message = helper.update_bank_detail(account_name, account_number, bank_account_id, bank)
          action = "updated"

       if message == None:
             messages.success(request, "Bank Account Detail's " + action +" Successfully")
       else:
            messages.error(request, message)
       return redirect('/bank_account/')
    
class Withdraw_amount(LoginRequiredMixin, View):
    login_url='/Auth/'

    def get(self, request):
      user_wallet = wallet.objects.get(user=request.user.id)
      user_bank_account = bank_detail.objects.filter(user__id=request.user.id)
      four_days_ago = timezone.now().date()- timedelta(days=4)
      Notifications = notification.objects.filter(user=request.user, created_at__gte=four_days_ago).order_by('-created_at')
      new_notification = notification.objects.filter(user=request.user, is_open=False).count()
      last_withdraw = None

      if user_bank_account:
         user_bank_account = bank_detail.objects.get(user__id=request.user.id)
      if withdraw.objects.filter(user__id=request.user.id, withdraw_request_at__date=timezone.now().date()):
         last_withdraw = int(20)

      Data = {
              'user_wallet': user_wallet, 
              'user_bank_account': user_bank_account, 
              'last_withdraw': last_withdraw,
              }
      if company_profile.objects.all():
         Company_profile = company_profile.objects.all().first()
         Data['Company_profile'] = Company_profile
      return render(request, 'withdraw.html', Data)
    
    def post(self, request, *args):
       data = request.POST
       amount = data.get('amount', None)
       bank_account = data.get('bank', None)
       bank_add = data.get('bank_add', None)
       four_second_ago = timezone.now() - timedelta(seconds=4)
       if bank_add == 'no':
           messages.success(request, "Please add your bank account first")
           return redirect('/bank_account/')
           
       if not user_plan.objects.filter(user=request.user, plan__price__gte=101):
           messages.error(request, "You need to buy atleast one plan, before withdraw request")
       elif withdraw.objects.filter(user=request.user, withdraw_request_at__gte=four_second_ago):
           messages.success(request, "Your withdraw request is submit successfully")
       else:
         message = withdraw.create_withdraw_request(int(amount), request.user, bank_account)
         if message == None:
               messages.success(request, "Your withdraw request is submit successfully")
         else:
               messages.error(request, message)
       return redirect('/withdraw/')

class Invest(LoginRequiredMixin, View):
   login_url='/Auth/'

   def get(self, request, *args):
      plans_days = []
      income_per_plan = []
      total_user_income = 0
      total= 0
      user_wallet = wallet.objects.get(user=request.user.id)
      User_plans = user_plan.objects.filter(user__id=request.user.id).order_by('-id')
      total_income = income.objects.filter(user__id=request.user.id, income_resource='My Investment Income')
      four_days_ago = timezone.now().date()- timedelta(days=4)
      Notifications = notification.objects.filter(user=request.user, created_at__gte=four_days_ago).order_by('-created_at')
      new_notification = notification.objects.filter(user=request.user, is_open=False).count()
      for j in total_income:
            total_user_income = total_user_income + j.amount
      total_user_income = round(total_user_income, 2)
      for i in User_plans:
         total_income = income.objects.filter(
                                               user__id=request.user.id, 
                                               income_resource='My Investment Income',
                                               user_plan=user_plan.objects.get(id=i.id),
                                               )
         for j in total_income:
              total = float(total + j.amount)
         income_per_plan.append(total)
         total= 0
         if i.status == 'In Process':
            time_diff = timezone.now() - i.started_at
            days_diff = int(time_diff.days +1)
            plans_days.append(days_diff)
         else:
            plans_days.append(i.plan.plan_duration)
      total_user_income = sum(income_per_plan)
      total_user_income = round(total_user_income, 2)
      User_plans_count = user_plan.objects.filter(user__id=request.user.id, status='In Process').count()

      Data = {
              'User_plans': User_plans, 
              'user_wallet': user_wallet, 
              'User_plans_count': User_plans_count,
              'total_user_income': total_user_income,
              'income_per_plan': income_per_plan,
              'plans_days': plans_days,
               'Notifications': Notifications, 
               'new_notification': new_notification
              }
      if company_profile.objects.all():
         Company_profile = company_profile.objects.all().first()
         Data['Company_profile'] = Company_profile
      return render(request, 'my_invest.html', Data)
   
   def post(self, request, *args):
      data = request.POST
      buy_plan = data.get('plan', None)
      message = user_plan.create_user_plan(buy_plan, request.user.id)
      if message == None:
         messages.success(request, "New Investment Plan Buy Successfully")
      else:
         messages.error(request, message)
      return redirect('/invest/')
   
class MyBills(LoginRequiredMixin, View):
    login_url='/Auth/'

    def get(self, request):
      user_wallet = wallet.objects.get(user=request.user.id)
      deposit_history = deposit.objects.filter(user=request.user.id).order_by('-id')
      withdraw_history = withdraw.objects.filter(user=request.user.id).order_by('-id')
      income_history = income.objects.filter(user=request.user.id).order_by('-id')
      four_days_ago = timezone.now().date()- timedelta(days=4)
      Notifications = notification.objects.filter(user=request.user, created_at__gte=four_days_ago).order_by('-created_at')
      new_notification = notification.objects.filter(user=request.user, is_open=False).count()



      paginator = Paginator(withdraw_history, 100)  # Show 10 contacts per page.
      page_number = request.GET.get('page')
      withdraw_history = paginator.get_page(page_number)

      
      Data = {
              'user_wallet': user_wallet, 
              'deposit_history': deposit_history, 
              'withdraw_history': withdraw_history, 
              'income_history': income_history,
               'Notifications': Notifications, 
               'new_notification': new_notification
              }
      if company_profile.objects.all():
         Company_profile = company_profile.objects.all().first()
         Data['Company_profile'] = Company_profile
      return render(request, 'history.html', Data)
    
class Profile(LoginRequiredMixin, View):
       login_url='/Auth/'

       def get(self, request, *args):
          user_wallet = wallet.objects.get(user=request.user.id)
          four_days_ago = timezone.now().date()- timedelta(days=4)
          Notifications = notification.objects.filter(user=request.user, created_at__gte=four_days_ago).order_by('-created_at')
          new_notification = notification.objects.filter(user=request.user, is_open=False).count()
          Data = { 
                  'user_wallet': user_wallet,
                  'Notifications': Notifications, 
                  'new_notification': new_notification
                  }
          if company_profile.objects.all():
            Company_profile = company_profile.objects.all().first()
            Data['Company_profile'] = Company_profile
          return render(request, 'user_profile.html', Data)
       
       def post(self, request, *args):
           data = request.POST
           email = data.get('email', None)
           username = data.get('username', None)
         #   image = request.FILES.get('images', None)
           current_password = data.get("current_password", None)
           new_password = data.get("new_password", None)
           user_profile = User.objects.get(id=request.user.id)

           if username:
               user_profile.username = username
               user_profile.save()
               messages.success(request, 'Profile Updated Successfully')
           elif current_password and new_password:
               message = change_password_validate(self,
                                                   user_profile.id,
                                                   current_password,
                                                   new_password 
                                                  )
               if message == None:
                  messages.success(request, "Your Password is change successfully")
               else:
                  messages.error(request, message)
           return redirect('/user_profile/')
       
class Team(LoginRequiredMixin, View):
       login_url='/Auth/'

       def get(self, request, *args):
          domainname = 'xindun.shop'
          user_wallet = wallet.objects.get(user=request.user.id)
          Level_1 = User.objects.filter(refer_parent=request.user)
          Level_2 = User.objects.filter(refer_parent__refer_parent=request.user)
          Level_3 = User.objects.filter(refer_parent__refer_parent__refer_parent=request.user)
          Level_1_count = User.objects.filter(refer_parent=request.user).count()
          Level_2_count = User.objects.filter(refer_parent__refer_parent=request.user).count()
          Level_3_count = User.objects.filter(refer_parent__refer_parent__refer_parent=request.user).count()
          four_days_ago = timezone.now().date()- timedelta(days=4)
          Notifications = notification.objects.filter(user=request.user, created_at__gte=four_days_ago).order_by('-created_at')
          new_notification = notification.objects.filter(user=request.user, is_open=False).count()
          total_income = Level_1_income = Level_2_income = Level_3_income = 0
          Level_1_income_per_refer = []
          Level_2_income_per_refer = []
          Level_3_income_per_refer = []
          Level_1_name = []
          Level_2_name = []
          Level_3_name = []
          success_deposit = deposit.objects.filter( 
                                                   Q(user__refer_parent=request.user) | 
                                                   Q(user__refer_parent__refer_parent=request.user) |
                                                   Q(user__refer_parent__refer_parent__refer_parent=request.user),
                                                   status='Deposit Success',)
          total_deposit = success_deposit.aggregate(total_refer_deposit=(Sum('amount')))
          team_size = User.objects.filter( Q(refer_parent=request.user) | 
                                      Q(refer_parent__refer_parent=request.user) |
                                      Q(refer_parent__refer_parent__refer_parent=request.user),
                                      ).count()
          for i in  Level_1:
              total = 0
              for j in income.objects.filter( Q(income_resource='Reference Income') |
                                              Q(income_resource='Reference Join Income'), 
                                             refer_user=i.id,
                                             user_level="Level 1"):
                 Level_1_income = float(Level_1_income + j.amount)
                 total = 0
                 for z in income.objects.filter(Q(income_resource='Reference Income') | 
                                                Q(income_resource='Reference Join Income'),
                                                  user_level="Level 1", 
                                                  refer_user=j.refer_user):
                   total = total + z.amount
              Level_1_income_per_refer.append(total)
              Level_1_name.append(convert_middle_to_asterisk(int(i.phone_number)))
          for i in  Level_2:
              total = 0
              for j in income.objects.filter(Q(income_resource='Reference Income') | 
                                             Q(income_resource='Reference Join Income'), 
                                             refer_user=i.id, 
                                             user_level="Level 2"):
                 Level_2_income = float(Level_2_income + j.amount)
                 total = 0
                 for z in income.objects.filter(Q(income_resource='Reference Income') | 
                                                Q(income_resource='Reference Join Income'), 
                                                refer_user=j.refer_user.id, 
                                                user_level="Level 2"):
                   total = total + z.amount
              Level_2_income_per_refer.append(total)
              Level_2_name.append(convert_middle_to_asterisk(int(i.phone_number)))


          for i in  Level_3:
              total = 0
              for j in income.objects.filter(Q(income_resource='Reference Income') | 
                                             Q(income_resource='Reference Join Income'), 
                                             refer_user=i.id, 
                                             user_level="Level 3"):
                 Level_3_income = float(Level_3_income + j.amount)
                 total = 0
                 for z in income.objects.filter(Q(income_resource='Reference Income') | 
                                                Q(income_resource='Reference Join Income'), 
                                                refer_user=j.refer_user.id, 
                                                user_level="Level 3"):
                   total = total + z.amount
              Level_3_income_per_refer.append(total)
              Level_3_name.append(convert_middle_to_asterisk(int(i.phone_number)))


          total_refer_income = income.objects.filter(Q(income_resource='Reference Income') | 
                                                     Q(income_resource='Reference Join Income'), 
                                                     user=request.user)
          for i in total_refer_income:
              total_income = float(i.amount + total_income)


          Data = {
                  'user_wallet': user_wallet, 
                  'Level_1_count': Level_1_count,
                  'Level_2_count': Level_2_count, 
                  "Level_3_count": Level_3_count,
                  "Level_1" : Level_1,
                  "Level_2" : Level_2,
                  "Level_3" : Level_3,
                  "Level_1_name" : Level_1_name,
                  "Level_2_name" : Level_2_name,
                  "Level_3_name" : Level_3_name,
                  "total_refer_income" : total_refer_income,
                  "team_size" : team_size,
                  "total_income" : total_income,
                  "total_refer_deposit": total_deposit['total_refer_deposit'],
                  "Level_1_income" : Level_1_income,
                  "Level_2_income" : Level_2_income,
                  "Level_3_income" : Level_3_income,
                  "Level_1_income_per_refer" : Level_1_income_per_refer,
                  "Level_2_income_per_refer" : Level_2_income_per_refer,
                  "Level_3_income_per_refer" : Level_3_income_per_refer,
                  'Notifications': Notifications, 
                  'new_notification': new_notification,
                  'domainname' : domainname,
                  }
          if company_profile.objects.all():
               Company_profile = company_profile.objects.all().first()
               Data['Company_profile'] = Company_profile
          return render(request, 'user_team.html', Data)

class Mine(LoginRequiredMixin, View):
    login_url = '/Auth/'   

    def get(self, request, *args):
          user_wallet = wallet.objects.get(user=request.user.id)
          four_days_ago = timezone.now().date()- timedelta(days=4)
          Notifications = notification.objects.filter(user=request.user, created_at__gte=four_days_ago).order_by('-created_at')
          new_notification = notification.objects.filter(user=request.user, is_open=False).count()
          Data = {
                  'user_wallet': user_wallet,
                  'Notifications': Notifications, 
                  'new_notification': new_notification
                  }
          if company_profile.objects.all():
               Company_profile = company_profile.objects.all().first()
               Data['Company_profile'] = Company_profile
          return render(request, 'Mine.html', Data)
    
class About_us(LoginRequiredMixin, View):
       login_url='/Auth/'

       def get(self, request, *args):
          user_wallet = wallet.objects.get(user=request.user.id)
          four_days_ago = timezone.now().date()- timedelta(days=4)
          Notifications = notification.objects.filter(user=request.user, created_at__gte=four_days_ago).order_by('-created_at')
          new_notification = notification.objects.filter(user=request.user, is_open=False).count()
          Data = {
                  'user_wallet': user_wallet, 
                  'Notifications': Notifications, 
                  'new_notification': new_notification
                  }
          if company_profile.objects.all():
            Company_profile = company_profile.objects.all().first()
            Data['Company_profile'] = Company_profile
          return render(request, 'about_us.html', Data)

class Our_services(LoginRequiredMixin, View):
       login_url='/Auth/'

       def get(self, request, *args):
          user_wallet = wallet.objects.get(user=request.user.id)
          four_days_ago = timezone.now().date()- timedelta(days=4)
          Notifications = notification.objects.filter(user=request.user, created_at__gte=four_days_ago).order_by('-created_at')
          new_notification = notification.objects.filter(user=request.user, is_open=False).count()
          Data = {
                  'user_wallet': user_wallet, 
                  'Notifications': Notifications, 
                  'new_notification': new_notification
                  }
          if company_profile.objects.all():
               Company_profile = company_profile.objects.all().first()
               Data['Company_profile'] = Company_profile
          if whatsapp_group_link.objects.all():
               Whatsapp_link = whatsapp_group_link.objects.all().first()
               Data['Whatsapp_link'] = Whatsapp_link
          return render(request, 'services.html', Data)
       
class initial_popup(LoginRequiredMixin, View):
    login_url='/Auth/'

    def get(self, request):
           # Check if the popup has already been shown
        if request.session.get('popup_shown', True):
            request.session['popup_shown'] = False
        return JsonResponse({'result': "show popup"})