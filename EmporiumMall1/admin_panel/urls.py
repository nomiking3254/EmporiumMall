from django.urls import path
from admin_panel.views import *

urlpatterns = [
   path('', dashboard.as_view()),
   path('view_notification/', admin_notification.as_view(), name='background_task'),
   path('deposit_Reject_approved/<int:id>/', deposit_Reject_approved.as_view(), name='deposit_Reject_approved'),
   path('withdraw_Reject_approved/<int:id>/', withdraw_Reject_approved.as_view(), name='withdraw_Reject_approved'),
   path('all_users/', view_all_users.as_view(), name='view_all_users'),
   path('user_deactivate_activate/<int:id>/', view_all_users.as_view(), name="user_deactivate_activate"),
   path('all_plans/', view_all_plans.as_view(), name='all_plans'),
   path('plan_deactivate_activate/<int:id>/', view_all_plans.as_view(), name="plan_deactivate_activate"),
   path('add_plan/',add_new_plan.as_view(), name='add_new_plan'),
   path('all_account/', bank_accounts.as_view(), name='bank_accounts'),
   path('update_plan/',view_all_plans.as_view(), name="update plan" ),
   
   path('update_account/', bank_accounts.as_view(), name='update_bank_account'),
   path('add_account/', add_new_bank_account.as_view(), name='add_account'),
   path('depost/', all_depost_requests.as_view(), name='all_depost_requests'),
   path('withdraw/', all_withdraw_requests.as_view(), name='all_withdraw_requests'),
   path('profile/', admin_profile.as_view(), name='admin_profile'),
   path('company_profile/', company_profiles.as_view(), name='company_profile'),
   path('socail_contact/', Contact_information.as_view(), name="Contact_information_setup")

]