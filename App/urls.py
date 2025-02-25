from django.urls import path
from App import views
from .views import  daily_report,monthly_report,AllsportWorker,Contract_list,day_report,Monthly_Report,Custom_Report,custom_reports

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'), 
    path('', views.user_login, name='login'),  
    path('sport_provider_dashboard/', views.sport_provider_dashboard, name='sport_provider_dashboard'),
    path('sport_provider_dashboard/check_customer/', views.check_customer, name='check_customer'),
     path('sport_provider_dashboard/daily-report/', daily_report, name='daily_report'),
     path('sport_provider_dashboard/monthly-report/', monthly_report, name='monthly_report'),
     path('sport_provider_dashboard/AllsportWorker/', AllsportWorker, name='AllsportWorker'),
    path('sport_provider_dashboard/Contract/', Contract_list, name='Contract'),
    path('sport_provider_dashboard/Custom_Reports/', custom_reports, name='Custom_Reports'),
# sport_partner_dashboard

    path('sport_partner_dashboard/', views.sport_partner_dashboard, name='sport_partner_dashboard'),
    path('sport_partner_dashboard/day_report/', day_report, name='day_report'),
    path('sport_partner_dashboard/Monthly_Report/', Monthly_Report, name='Monthly_Report'),
    path('sport_partner_dashboard/Custom_Report/', Custom_Report, name='Custom_Report'),
    
]
