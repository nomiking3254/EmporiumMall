from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin as CommonLoginRequiredMixin
from account.helper import update_bank_detail, update_bank_detail, update_plan_detail
from account.models import add_bank, plan, user_plan, deposit, wallet, withdraw, bank_detail
from auths.helper import change_password_validate
from auths.models import User
from django.views import View
from django.contrib import messages
from admin_panel.helper import approve_reject_deposit, approve_reject_withdraw, user_deactivate_activate, \
    plan_deactivate_activate, update_company_profile, update_social_media_link
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from admin_panel.models import company_profile, whatsapp_group_link
from users.models import notification
from django.utils import timezone
from datetime import timedelta
from auths.helper import AdminLoginRequiredMixin as LoginRequiredMixin

# Create your views here.
class dashboard(LoginRequiredMixin, View):

    def get(self, request):
       total_deposit = 0
       total_Withdraw = 0
       total_deposit_request = deposit.objects.filter(status='Pending').count()
       total_withdraw_request = withdraw.objects.filter(status='Pending').count()
       total_user = User.objects.filter(is_superuser=False).count()
       total_plans = plan.objects.all().count()
       total_buy_plans = user_plan.objects.all().count()
       deposit_request = deposit.objects.filter(status='Pending')
       Withdraw_request = withdraw.objects.filter(status='Pending')
       Wallet = wallet.objects.all() 
       four_days_ago = timezone.now().date()- timedelta(days=4)
       Notifications = notification.objects.filter(user=request.user, created_at__gte=four_days_ago).order_by('-created_at')
       new_notification = notification.objects.filter(user=request.user, is_open=False).count()
       for i in deposit.objects.filter(status='Deposit Success'):
           total_deposit = total_deposit + i.amount

       for i in withdraw.objects.filter(status='Withdraw Success'):
            total_Withdraw = total_Withdraw + i.withdraw_amount
            
       Data = {
              'total_deposit_request' : total_deposit_request, 
               "total_withdraw_request" : total_withdraw_request,
               "total_deposit" : total_deposit,
               "total_Withdraw" : total_Withdraw,
               "total_plans" : total_plans,
               "total_buy_plans" : total_buy_plans,
               "total_user" : total_user,
               "deposit_request" : deposit_request,
               "Withdraw_request": Withdraw_request,
               "Wallet" : Wallet,
               "Notifications" : Notifications,
               "new_notification" : new_notification
               }
       if company_profile.objects.all():
            Company_profile = company_profile.objects.all().first()
            Data['Company_profile'] = Company_profile
       return render(request, 'admin_dashboard.html', Data)
    
class admin_notification(CommonLoginRequiredMixin, View):
    login_url='/Auth/'

    def get(self, request):
        # Perform background task here
        result = "Background task completed"
        admin_notifications = notification.objects.filter(is_open=False, user=request.user)
        for i in admin_notifications:
            admin_notification = notification.objects.get(id=i.id)
            admin_notification.is_open = True
            admin_notification.save()
        return JsonResponse({'result': result})
    
class deposit_Reject_approved(LoginRequiredMixin, View):
    login_url='/Auth/'

    def post(self, request, *arg, id=None):
          data = request.POST
          decision = data.get('action', None)
          message = approve_reject_deposit(decision, id)
          if message == None:
              messages.success(request, "Deposit request is " + decision + " successfully" )
          else:
              messages.error(request, message)
          return redirect('/admin_dashboard/')

class withdraw_Reject_approved(LoginRequiredMixin, View):
    login_url='/Auth/'

    def post(self, request, *arg, id=None):
          data = request.POST
          decision = data.get('action', None)
          message = approve_reject_withdraw(decision, id)
          if message == None:
              messages.success(request, "Withdraw request is " + decision + "  successfully" )
          else:
              messages.error(request, message)
          return redirect('/admin_dashboard/')
    
class view_all_users(LoginRequiredMixin, View):
    login_url='/Auth/'
   
    def get(self, request):
      user = User.objects.filter(is_superuser=False).order_by('date_joined')
      four_days_ago = timezone.now().date()- timedelta(days=4)
      Notifications = notification.objects.filter(user=request.user, created_at__gte=four_days_ago).order_by('-created_at')
      new_notification = notification.objects.filter(user=request.user, is_open=False).count()
      Data ={
             'user' : user,
             "Notifications" : Notifications,
             "new_notification" : new_notification,
             }
      if company_profile.objects.all():
            Company_profile = company_profile.objects.all().first()
            Data['Company_profile'] = Company_profile
      return render(request, 'view_all_users.html', Data)
    
    def post(self, request, *arg, id=None):
          data = request.POST
          decision = data.get('action', None)
          message = user_deactivate_activate(decision, id)
          if message == None:
              messages.success(request,"User account is " + decision +" successfully" )
          else:
              messages.error(request, message)
          return redirect('/admin_dashboard/all_users/')
        
class view_all_plans(LoginRequiredMixin, View):
    login_url='/Auth/'
   
    def get(self, request):
      all_plans = plan.objects.all().order_by('price')
      four_days_ago = timezone.now().date()- timedelta(days=4)
      Notifications = notification.objects.filter(user=request.user, created_at__gte=four_days_ago).order_by('-created_at')
      new_notification = notification.objects.filter(user=request.user, is_open=False).count()
      Data ={  
              'all_plans' : all_plans,
               "Notifications" : Notifications,
               "new_notification" : new_notification,
            }
      if company_profile.objects.all():
            Company_profile = company_profile.objects.all().first()
            Data['Company_profile'] = Company_profile
      return render(request, 'view_all_plans.html', Data)
    
    def post(self, request, *arg, id=None):
          data = request.POST
          decision = data.get('action', None)
          four_days_ago = timezone.now().date()- timedelta(days=4)
          Notifications = notification.objects.filter(user=request.user, created_at__gte=four_days_ago).order_by('-created_at')
          new_notification = notification.objects.filter(user=request.user, is_open=False).count()
          plan_id = data.get('id', None)
          if decision == 'update-btn':
            update_plan = plan.objects.get(id=plan_id)
            Data = {'update_plan': update_plan,
                    "Notifications" : Notifications,
                     "new_notification" : new_notification,
                    }
            if company_profile.objects.all():
                Company_profile = company_profile.objects.all().first()
                Data['Company_profile'] = Company_profile
            return render(request, 'update_plan.html', Data)
          elif decision == 'update-plan':
                plan_name = data.get('plan_name', None)
                plan_price = data.get('plan_price', None)
                total_income = data.get('total_income', None)
                duration = data.get('duration', None)
                lanuch = data.get('lanuch', False)
                quantity = data.get('quantity', None)
                plan_category = data.get('Category', None)
                image = request.FILES.get('plan_img', None)
                message = update_plan_detail(
                                              plan_name, 
                                              plan_price,  
                                              total_income, 
                                              duration, 
                                              lanuch, 
                                              quantity, 
                                              plan_id,
                                              plan_category,
                                              image
                                            )
                if message == None:
                    messages.success(request, "Plan is Updated successfully")
                    return redirect('/admin_dashboard/all_plans/')
                else:
                    messages.error(request, message)
          else:
            message = plan_deactivate_activate(decision, id)
            if message == None:
                messages.success(request,"Plan is " + decision +" successfully" )
            else:
                messages.error(request, message)
          return redirect('/admin_dashboard/all_plans/')
    
class add_new_plan(LoginRequiredMixin, View):
    login_url = '/Auth/'

    def get(self, request):
        four_days_ago = timezone.now().date()- timedelta(days=4)
        Notifications = notification.objects.filter(user=request.user, created_at__gte=four_days_ago).order_by('-created_at')
        new_notification = notification.objects.filter(user=request.user, is_open=False).count()
        Data = {"Notifications" : Notifications, "new_notification" : new_notification,}
        if company_profile.objects.all():
            Company_profile = company_profile.objects.all().first()
            Data['Company_profile'] = Company_profile
        return render(request, 'add_new_plan.html', Data)
    
    def post(self, request):
        data = request.POST
        plan_name = data.get('plan_name', None)
        plan_price = data.get('plan_price', None)
        total_income = data.get('total_income', None)
        duration = data.get('duration', None)
        lanuch = data.get('lanuch', False)
        quantity = data.get('quantity', None)
        image = request.FILES.get('plan_img', None)
        Category = data.get('Category', None)
        message = plan.create_new_plan(
                                plan_name, 
                                plan_price,  
                                total_income, 
                                duration, 
                                lanuch, 
                                quantity,
                                image,
                                Category
                            )
        if message == None:
           messages.success(request, "New Plan is added successfully")
           return redirect('/admin_dashboard/all_plans/')
        else:
           messages.error(request, message)
        return redirect('/admin_dashboard/add_plan/')

class bank_accounts(LoginRequiredMixin, View):
    login_url = '/Auth/'

    def get(self, request):
        admin_accounts = bank_detail.objects.filter(user__is_superuser=True)
        four_days_ago = timezone.now().date()- timedelta(days=4)
        Notifications = notification.objects.filter(user=request.user, created_at__gte=four_days_ago).order_by('-created_at')
        new_notification = notification.objects.filter(user=request.user, is_open=False).count()
        bank_names = add_bank.objects.all()
        Data = {'admin_accounts' : admin_accounts,
                "Notifications" : Notifications,
                "new_notification" : new_notification,
                "bank_names" : bank_names,
                }
        if company_profile.objects.all():
            Company_profile = company_profile.objects.all().first()
            Data['Company_profile'] = Company_profile
        return render(request, 'view_all_bank_accounts.html', Data)
    
    def post(self, request):
        data = request.POST
        action = data.get('action', None)
        id = data.get('id', None)

        try:
          update_account = bank_detail.objects.get(id=id)
          four_days_ago = timezone.now().date()- timedelta(days=4)
          Notifications = notification.objects.filter(user=request.user, created_at__gte=four_days_ago).order_by('-created_at')
          new_notification = notification.objects.filter(user=request.user, is_open=False).count()
          bank_names = add_bank.objects.all()
          if action == 'update-btn':
            Data = {'update_account': update_account,
                "Notifications" : Notifications,
                "new_notification" : new_notification,
                "bank_names" : bank_names,
                }
            if company_profile.objects.all():
                Company_profile = company_profile.objects.all().first()
                Data['Company_profile'] = Company_profile
            return render(request, 'update_bank_account.html', Data)
          else:
            account_name = data.get('account_name', None)
            account_number = data.get('account_number', None)
            bank = data.get('bank', None)
            message = update_bank_detail(account_name, account_number, id, bank)
            if message != None:
                messages.success(request, message)
                return redirect('/admin_dashboard/all_account/')

        except ObjectDoesNotExist as e:
            messages.error(request, e)
            return redirect('/admin_dashboard/all_account/')

        messages.success(request, "Your bank account is updated successfully")
        return redirect('/admin_dashboard/all_account/')

class add_new_bank_account(LoginRequiredMixin, View):
    login_url = '/Auth/'

    def get(self, request):
        Data = {}
        four_days_ago = timezone.now().date()- timedelta(days=4)
        Notifications = notification.objects.filter(user=request.user, created_at__gte=four_days_ago).order_by('-created_at')
        new_notification = notification.objects.filter(user=request.user, is_open=False).count()
        bank_names = add_bank.objects.all()
        Data = { 
                "Notifications" : Notifications, 
                "new_notification" : new_notification, 
                "bank_names" : bank_names,
                }
        if company_profile.objects.all():
            Company_profile = company_profile.objects.all().first()
            Data['Company_profile'] = Company_profile
        return render(request, 'add_new_bank_account.html', Data)
    
    def post(self, request):
        data = request.POST
        account_name = data.get('account_name', None)
        account_number = data.get('account_number', None)
        bank = data.get('bank', None)
        message = bank_detail.create_bank_detail(account_name, account_number, request.user, bank)
        if message == None:
            messages.success(request, 'New bank account is added successfully')
            return redirect('/admin_dashboard/all_account/')
        else:
            messages.error(request, message)
        return redirect('/admin_dashboard/add_account/')
    
class all_depost_requests(LoginRequiredMixin,View):
    login_url = '/Auth/'

    def get(self, request):
        deposit_request = deposit.objects.all().order_by('-deposit_request_at')
        four_days_ago = timezone.now().date()- timedelta(days=4)
        Notifications = notification.objects.filter(user=request.user, created_at__gte=four_days_ago).order_by('-created_at')
        new_notification = notification.objects.filter(user=request.user, is_open=False).count()
        Data = {
                'deposit_request': deposit_request,
                "Notifications" : Notifications,
                "new_notification" : new_notification,
                }
        if company_profile.objects.all():
            Company_profile = company_profile.objects.all().first()
            Data['Company_profile'] = Company_profile
        return render(request, 'view_all_deposit_request.html', Data)
    
    def post(self, request):
        data = request.POST
        decision = data.get('action', None)
        id = data.get('deposit_id', None)
        message = approve_reject_deposit(decision, id)
        if message == None:
            messages.success(request, "Deposit request is " + decision +" successfully" )
        else:
            messages.error(request, message)
        return redirect('/admin_dashboard/depost/')
    
class all_withdraw_requests(LoginRequiredMixin,View):
    login_url = '/Auth/'

    def get(self, request):
        Withdraw_request = withdraw.objects.all().order_by('-withdraw_request_at')
        four_days_ago = timezone.now().date()- timedelta(days=4)
        Notifications = notification.objects.filter(user=request.user, created_at__gte=four_days_ago).order_by('-created_at')
        new_notification = notification.objects.filter(user=request.user, is_open=False).count()
        Data = {
               'Withdraw_request': Withdraw_request,
                "Notifications" : Notifications,
                "new_notification" : new_notification,
                }
        if company_profile.objects.all():
            Company_profile = company_profile.objects.all().first()
            Data['Company_profile'] = Company_profile
        return render(request, 'view_all_withdraw_requests.html', Data)
    
    def post(self, request):
         data = request.POST
         decision = data.get('action', None)
         id = data.get('withdraw_id', None)
         message = approve_reject_withdraw(decision, id)
         if message == None:
              messages.success(request, "Withdraw request is " + decision +" successfully" )
         else:
              messages.error(request, message)
         return redirect('/admin_dashboard/withdraw/')
    
class admin_profile(LoginRequiredMixin,View):
    login_url = '/Auth/'

    def get(self, request):
        four_days_ago = timezone.now().date()- timedelta(days=4)
        Notifications = notification.objects.filter(user=request.user, created_at__gte=four_days_ago).order_by('-created_at')
        new_notification = notification.objects.filter(user=request.user, is_open=False).count()
        Data = {"Notifications" : Notifications, "new_notification" : new_notification}
        if company_profile.objects.all():
            Company_profile = company_profile.objects.all().first()
            Data['Company_profile'] = Company_profile
        return render(request, 'admin_profile.html', Data)
    
    def post(self, request):
           data = request.POST
           email = data.get('email', None)
           username = data.get('username', None)
           image = request.FILES.get('image', None)
           current_password = data.get("current_password", None)
           new_password = data.get("new_password", None)
           phone = data.get('phone', None)
           user_profile = User.objects.get(id=request.user.id)

           if email:
               if request.user.email == email:
                    user_profile.email = email
               elif User.objects.filter(email=email):
                    messages.error(request, 'email is already exist, email address is not updated')
                    return redirect('/admin_dashboard/profile/')
               user_profile.email = email
               user_profile.save()
               messages.success(request, 'Email is updated successfully')
           elif username:
               user_profile.username = username
               user_profile.save()
               messages.success(request, 'Username is updated successfully')
           elif phone:
               if User.objects.filter(phone_number=phone):
                    messages.error(request, 'Phone number is already exist')
                    return redirect('/admin_dashboard/profile/')
               user_profile.phone_number = phone
               user_profile.save()
               messages.success(request, 'Phone Number is updated successfully')
           elif image:
               user_profile.image = image
               user_profile.save()
               messages.success(request, 'Profile image is updated successfully')
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
           return redirect('/admin_dashboard/profile/')
    
class company_profiles(LoginRequiredMixin,View):
    login_url = '/Auth/'

    def get(self, request):
        four_days_ago = timezone.now().date()- timedelta(days=4)
        Notifications = notification.objects.filter(user=request.user, created_at__gte=four_days_ago).order_by('-created_at')
        new_notification = notification.objects.filter(user=request.user, is_open=False).count()
        Data = {"Notifications" : Notifications, "new_notification" : new_notification}
        if company_profile.objects.all():
            Company_profile = company_profile.objects.all().first()
            Data ={'Company_profile': Company_profile}
        return render(request, 'company_profile.html', Data)

    def post(self, request):
           data = request.POST
           company_name = data.get('company_name', None)
           company_address = data.get('company_address', None)
           company_logo = request.FILES.get('company_logo', None)
           action = data.get("action", None)
           if action == 'add':
               message = company_profile.create_company_profile(company_name, company_logo, company_address)
               if message == None:
                   messages.success(request, 'Company Profile is created successfully')
               else:
                   messages.error(request, message)
           elif action == 'update':
               id = data.get('id', None)
               message = update_company_profile(company_name, company_logo, company_address, id)
               if message == None:
                  messages.success(request, "You company profile is update successfully" )
               else:
                  messages.error(request, message)
           return redirect('/admin_dashboard/company_profile/')
    
class Contact_information(LoginRequiredMixin,View):
    login_url = '/Auth/'

    def get(self, request):
        four_days_ago = timezone.now().date()- timedelta(days=4)
        Notifications = notification.objects.filter(user=request.user, created_at__gte=four_days_ago).order_by('-created_at')
        new_notification = notification.objects.filter(user=request.user, is_open=False).count()
        Data = {"Notifications" : Notifications, "new_notification" : new_notification}
        if company_profile.objects.all():
            Company_profile = company_profile.objects.all().first()
            Data ={'Company_profile': Company_profile}
        if whatsapp_group_link.objects.all():
            Whatsapp_link = whatsapp_group_link.objects.all().first()
            Data['Whatsapp_link'] = Whatsapp_link
        return render(request, 'setup_contact_info.html', Data)

    def post(self, request):
        data = request.POST
        phone_number = data.get('phone', None)
        join_link = data.get('join_link', None)
        action = data.get("action", None)
        if action == 'add':
            message = whatsapp_group_link.create_social_media_link(join_link, phone_number)
            if message == None:
                 messages.success(request, "New Contact information is save successfully")
            else:
                 messages.error(request, message)
        elif action == 'update':
               id = data.get('id', None)
               message = update_social_media_link(join_link,phone_number, id)
               if message == None:
                  messages.success(request, "You Contact information is update successfully" )
               else:
                  messages.error(request, message)
        return redirect('/admin_dashboard/socail_contact/')
