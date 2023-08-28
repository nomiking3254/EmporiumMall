import uuid
from django.shortcuts import redirect, render
from django.contrib.auth import login
from django.views import View
from django.contrib import messages
from admin_panel.models import company_profile
from auths import helper
from auths.models import User
from auths.helper import RequiredLoginRequiredMixin

    
class Login(RequiredLoginRequiredMixin, View):

    def get(self, request):
        Data = {}
        if company_profile.objects.all():
            Company_profile = company_profile.objects.all().first()
            Data['Company_profile'] = Company_profile
        return render(request, 'login.html', Data)
    
    def post(self, request):
            Data = request.POST
            phone = Data.get('phone')
            Password = Data.get('password')
            message, user = helper.login_validate(phone, Password)
            if message != None:
                messages.error(request, message)
                return redirect('/Auth/')
            else:
                login(request, user)
                if request.user.is_superuser:
                  return redirect('/admin_dashboard/')
                else:
                  request.session['popup_shown'] = True
                  return redirect('/')

class Sign_Up(RequiredLoginRequiredMixin, View):

    def get(self, request, refer_code=''):
        Data = {'refer_code': refer_code}
        if company_profile.objects.all():
            Company_profile = company_profile.objects.all().first()
            Data['Company_profile'] = Company_profile
        return render(request, 'signup.html', Data)
    
    def post(self, request):
        Data = request.POST
        phone = Data.get('phone')
        password = Data.get('password')
        email = Data.get('email', None)
        reference = Data.get('reference', None)
        user_email = User.objects.filter(email=email)
        if user_email:
            message = "Email is already used"
            messages.error(request, message)
            return redirect('/Auth/signup/')
        if reference !="":
            refer_user, message = helper.is_valid_refer_code(reference)
            if message != None:
               messages.error(request, message)
               return redirect('/Auth/signup/' + reference +'/')
            else:
               reference = refer_user
        else:
            reference = None
        message = helper.validate_data(phone, email)
        if message != None:
            messages.error(request, message)
        else:
            User.create_user(phone, password, reference, email)
            messages.success(request, "Your Account is created successfully. Please login now")
            return redirect('/Auth/')
        return redirect('/Auth/signup/')
    

class Forgetpassword(RequiredLoginRequiredMixin, View):

    def get(self, request):
        return render(request, 'forgetpassword.html')
    
    def post(self, request):
            Data = request.POST
            phone = Data.get('phone')
            email = Data.get('email', None)

            if User.objects.filter(phone_number=phone, email=email).exists():
                user_data = User.objects.get(phone_number=phone, email=email)
                user_data.forget_password = uuid.uuid4()
                forgetPassword = user_data.forget_password
                user_data.save()
                return render(request, 'changepassword.html', {"forgetPassword": forgetPassword})
            messages.error(request, "Invalid Phone number or Email")
            return render(request, 'forgetpassword.html')


class Changepassword(View):

    def get(self, request):
        return redirect('/Auth/forgetpassword/')
    
    def post(self, request):
         Data = request.POST
         new_password = Data.get('password', None)
         forgetPassword = Data.get('forgetPassword', None)

         if new_password and forgetPassword:
            if User.objects.filter(forget_password=forgetPassword).exists():
                user = User.objects.get(forget_password=forgetPassword)
                user.set_password(new_password)
                user.forget_password = uuid.uuid4()
                user.save()
                messages.success(request, 'Password is changed successfully, please login now')   
                return redirect('/Auth/')   
         return redirect('/Auth/forgetpassword/')

