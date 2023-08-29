from django.urls import path
from users import views

urlpatterns = [
    path('', views.Home.as_view(), name="user_home_page"),
    path('bank_account/', views.Bank_amount_setting.as_view(), name="bank_account_page"),
    path('invest/', views.Invest.as_view(), name='user_inest_plans'),
    path('recharge/', views.Recharge.as_view(), name='recharge_page'),
    path('withdraw/', views.Withdraw_amount.as_view(), name='withdraw_page'),
    path('bill/', views.MyBills.as_view(), name='My_bill_history'),
    path('user_profile/', views.Profile.as_view(), name="User_profile_page"),
    path('user_team/', views.Team.as_view(), name="user_reference_team"),
    path('mine/', views.Mine.as_view(), name='about_us_page'),
    path('about_us/', views.About_us.as_view(), name='about_us_page'),
    path('services/', views.Our_services.as_view(), name="Our_services"),
    path('popup/intial/', views.initial_popup.as_view()),
    path('plan_threagh/',views.plan_income.as_view())
]