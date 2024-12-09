"""first_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from first_app import views
from django.contrib import admin


app_name = 'first_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('utilization/<str:region>/', views.utilization, name='utilization'),
    path('tables/', views.tables, name='tables'),
    path('attrition/<str:region>/', views.attrition, name='attrition'),
    path('headcount/<str:region>/', views.headcount, name='headcount'),
    path('attendance/<str:region>/', views.attendance, name='attendance'),
    path('login/', views.login, name='login'),
    # path('emea_attendance/', views.emea_attendance, name='emea_attendance'),
    # path('usca_attendance/', views.usca_attendance, name='usca_attendance'),
    path('admin/', admin.site.urls),
    path('fetch_firstname/', views.fetch_firstname, name='fetch_firstname'),
    path('tenure_by_department/', views.tenure_by_department, name='tenure_by_department'),
    path('dynamic_change_attrition/', views.dynamic_change_attrition, name='dynamic_change_attrition'),
    path('attrition_by_tenure_by_department/', views.attrition_by_tenure_by_department, name='attrition_by_tenure_by_department'),
    
    path('get_assoc_managers/', views.get_assoc_managers, name='get_assoc_managers'),
    path('get_team_leads/', views.get_team_leads, name='get_team_leads'),
    path('get_teams/', views.get_teams, name='get_teams'),
    path('get_computations/', views.get_computations, name='get_computations'),
    path('fil_utilization/', views.fil_utilization, name='fil_utilization'),
    path('fil_utilization_cat_member/', views.fil_utilization_cat_member, name='fil_utilization_cat_member'),
    path('category_filter/', views.category_filter, name='category_filter'),
    path('weekly_util_with_country/', views.weekly_util_with_country, name='weekly_util_with_country'),
    path('monthly_util_with_team/', views.monthly_util_with_team, name='monthly_util_with_team'),
    path('performance/', views.performance, name='performance'),
    path('get_break_adherence_drilldown/', views.get_break_adherence_drilldown, name='get_break_adherence_drilldown'),
    # path('delivery/<str:region>/', views.delivery, name='delivery'),
    path('quality/<str:region>/', views.quality, name='quality'),
    path('quality_percentage_country/', views.quality_percentage_country, name='quality_percentage_country'),
    path('quality_percentage_per_country_bcr/', views.quality_percentage_per_country_bcr, name='quality_percentage_per_country_bcr'),
    path('service_delivery/<str:region>/', views.service_delivery, name='service_delivery'),
    path('service_late_reason_per_country/', views.service_late_reason_per_country, name='service_late_reason_per_country'),
    path('service_delivery_bu_code/', views.service_delivery_bu_code, name='service_delivery_bu_code'),

    path('productivity/<str:region>/', views.productivity, name='productivity'),
    path('productivity_per_region_drilleddown/', views.productivity_per_region_drilleddown, name='productivity_per_region_drilleddown'),
    path('local_management_per_manager_volume_click/', views.local_management_per_manager_volume_click, name='local_management_per_manager_volume_click'),
    path('local_management_per_manager_volume_click_drilldown/', views.local_management_per_manager_volume_click_drilldown, name='local_management_per_manager_volume_click_drilldown'),
    path('local_management_per_manager_productivity_click/', views.local_management_per_manager_productivity_click, name='local_management_per_manager_productivity_click'),
    path('local_management_per_manager_productivity_click_drilldown/', views.local_management_per_manager_productivity_click_drilldown, name='local_management_per_manager_productivity_click_drilldown'),
    
    path('rax_utilization/<str:region>/', views.rax_utilization, name='rax_utilization'),
    path('rax_util_team/', views.rax_util_team, name='rax_util_team'),
    path('rax_util_team_hours/', views.rax_util_team_hours, name='rax_util_team_hours'),
    path('overall_rax_utilization_per_team/', views.overall_rax_utilization_per_team, name='overall_rax_utilization_per_team'),
    path('quality_report/<str:region>/', views.quality_report, name='quality_report'),
    path('pages_contact', views.pages_contact, name='pages_contact'),
    # path('top_management/', views.top_management, name='top_management'),
    
    # path('rax_analyst_utilization/', views.rax_analyst_utilization, name='rax_analyst_utilization'),

    


    


    
    
    

]


