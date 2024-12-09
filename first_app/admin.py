from django.contrib import admin
from . models import MasterList
from . models import CFunction
from . models import Attrition
from . models import MovementType, MasterListFileUpload, Reason, AttritionListFileUpload, Attendance, Attendance_FileUpload, Productivity, Productivity_FileUpload
from . models import  Supervisor_APAC, Supervisor_EMEA, Supervisor_emea_fileupload, Supervisor_USCA, Supervisor_usca_fileupload
from . models import  Utilization, Utilization_FileUpload, Quality, Quality_FileUpload, Service_Delivery, Service_Delivery_FileUpload, Rax_Utilization, Rax_Utilization_FileUpload, Quality_Report, Quality_Report_FileUpload
from functools import reduce
from django.db.models import Q

from django.urls import reverse
from django.utils.html import format_html
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION

from simple_history.admin import SimpleHistoryAdmin
from django.http import Http404
from django.urls import reverse
from django.utils.html import format_html
from urllib.parse import unquote
from django.utils.encoding import force_str
from django.utils.html import escape
from django.utils.translation import gettext as _
from django.utils.html import format_html
from dal import autocomplete




class MasterListModelAdmin(SimpleHistoryAdmin, admin.ModelAdmin):
    search_fields = ['emp_id', 'firstname','lastname']
    list_display = ['emp_id', 'firstname','lastname','grade','job_title','job_family','location','manager_name', 'tier_5','region',
                    'hire_date','show_history_link']  # Specify the fields to display in the table
    list_per_page = 50  # Set the number of records to display per page
    ordering = ['region','hire_date']  # Specify the field to sort on
    # history_list_display = ["changed_fields","list_changes"]
    history_list_display = ["changed_fields"]

    
    
    def get_search_results(self, request, queryset, search_term):
        # Override the default search behavior
        search_fields = self.get_search_fields(request)
        if search_fields and search_term:
            search_terms = search_term.split()
            search_queries = [Q(**{field + '__icontains': term}) for term in search_terms for field in search_fields]
            queryset = queryset.filter(reduce(lambda x, y: x | y, search_queries))
        return queryset, False
    
    def show_history_link(self, obj):
        url = reverse('admin:{}_{}_history'.format(obj._meta.app_label, obj._meta.model_name), args=[obj.pk])
        return format_html('<a href="{}">History</a>', url)
    show_history_link.short_description = 'History'

    def changed_fields(self, obj):
        if obj.prev_record:
            delta = obj.diff_against(obj.prev_record)
            return delta.changed_fields
        return None

    

    

admin.site.register(MasterList,MasterListModelAdmin)

  




    
   


class MasterListFileUploadAdmin(admin.ModelAdmin):
    list_display = ['id','file', 'upload_timestamp']  # Specify the fields to display in the table
    list_per_page = 20  # Set the number of records to display per page

    readonly_fields = ['upload_timestamp']

    def save_model(self, request, obj, form, change):
        obj.save(request=request)

    

admin.site.register(MasterListFileUpload, MasterListFileUploadAdmin)






class Attendance_ModelAdmin(SimpleHistoryAdmin, admin.ModelAdmin):
    # search_fields = ['prod_analyst','start_time', 'end_time']
    list_display = ['att_date', 'emp_id','emp_name','site','team','tlead','assoc_manager','prod_manager','country','region','status','type','reason','upload','show_history_link']  # Specify the fields to display in the table
    list_per_page = 700  # Set the number of records to display per page
    history_list_display = ["changed_fields","list_changes"]
    
    def show_history_link(self, obj):
        url = reverse('admin:{}_{}_history'.format(obj._meta.app_label, obj._meta.model_name), args=[obj.pk])
        return format_html('<a href="{}">History</a>', url)
    show_history_link.short_description = 'History'

admin.site.register(Attendance,Attendance_ModelAdmin)

class Attendance_FileUploadAdmin(admin.ModelAdmin):
    list_display = ['id','file', 'upload_timestamp']  # Specify the fields to display in the table
    list_per_page = 20  # Set the number of records to display per page

    readonly_fields = ['upload_timestamp']

    def save_model(self, request, obj, form, change):
        obj.save(request=request)

admin.site.register(Attendance_FileUpload, Attendance_FileUploadAdmin)

class Supervisor_APAC_ModelAdmin(SimpleHistoryAdmin, admin.ModelAdmin):
    search_fields = ['team_name', 'production_manager','associate_manager']
    list_display = ['team_name', 'production_manager','associate_manager','show_history_link']  # Specify the fields to display in the table
    list_per_page = 50  # Set the number of records to display per page
    ordering = ['team_name']  # Specify the field to sort on
    history_list_display = ["changed_fields","list_changes"]

    def show_history_link(self, obj):
        url = reverse('admin:{}_{}_history'.format(obj._meta.app_label, obj._meta.model_name), args=[obj.pk])
        return format_html('<a href="{}">History</a>', url)
    show_history_link.short_description = 'History'

    def changed_fields(self, obj):
        if obj.prev_record:
            delta = obj.diff_against(obj.prev_record)
            return delta.changed_fields
        return None

admin.site.register(Supervisor_APAC,Supervisor_APAC_ModelAdmin)

class Supervisor_EMEA_ModelAdmin(SimpleHistoryAdmin, admin.ModelAdmin):
    search_fields = ['team_name', 'production_manager','associate_manager']
    list_display = ['team_name', 'production_manager','associate_manager','show_history_link']  # Specify the fields to display in the table
    list_per_page = 50  # Set the number of records to display per page
    ordering = ['team_name']  # Specify the field to sort on
    history_list_display = ["changed_fields","list_changes"]

    def show_history_link(self, obj):
        url = reverse('admin:{}_{}_history'.format(obj._meta.app_label, obj._meta.model_name), args=[obj.pk])
        return format_html('<a href="{}">History</a>', url)
    show_history_link.short_description = 'History'

    def changed_fields(self, obj):
        if obj.prev_record:
            delta = obj.diff_against(obj.prev_record)
            return delta.changed_fields
        return None

admin.site.register(Supervisor_EMEA,Supervisor_EMEA_ModelAdmin)

class EMEA_Supervisor_FileUploadAdmin(admin.ModelAdmin):
    list_display = ['id','file', 'upload_timestamp']  # Specify the fields to display in the table
    list_per_page = 20  # Set the number of records to display per page

    readonly_fields = ['upload_timestamp']

    def save_model(self, request, obj, form, change):
        obj.save(request=request)

admin.site.register(Supervisor_emea_fileupload, EMEA_Supervisor_FileUploadAdmin)


class Supervisor_USCA_ModelAdmin(SimpleHistoryAdmin, admin.ModelAdmin):
    search_fields = ['team_name', 'production_manager','associate_manager']
    list_display = ['team_name', 'production_manager','associate_manager','show_history_link']  # Specify the fields to display in the table
    list_per_page = 50  # Set the number of records to display per page
    ordering = ['team_name']  # Specify the field to sort on
    history_list_display = ["changed_fields","list_changes"]

    def show_history_link(self, obj):
        url = reverse('admin:{}_{}_history'.format(obj._meta.app_label, obj._meta.model_name), args=[obj.pk])
        return format_html('<a href="{}">History</a>', url)
    show_history_link.short_description = 'History'

    def changed_fields(self, obj):
        if obj.prev_record:
            delta = obj.diff_against(obj.prev_record)
            return delta.changed_fields
        return None

admin.site.register(Supervisor_USCA,Supervisor_USCA_ModelAdmin)

class USCA_Supervisor_FileUploadAdmin(admin.ModelAdmin):
    list_display = ['id','file', 'upload_timestamp']  # Specify the fields to display in the table
    list_per_page = 20  # Set the number of records to display per page

    readonly_fields = ['upload_timestamp']

    def save_model(self, request, obj, form, change):
        obj.save(request=request)

admin.site.register(Supervisor_usca_fileupload, USCA_Supervisor_FileUploadAdmin)


class Utilization_ModelAdmin(SimpleHistoryAdmin, admin.ModelAdmin):

    search_fields = ['region','user', 'name','team','subtask','quantity', 'country']
    list_display = ['region','user', 'name', 'team', 'country', 'subtask', 'quantity', 'time_spent_in_min', 'shift_start', 'duration_hour',
                    'week', 'show_history_link']  # Specify the fields to display in the table
    list_per_page = 700  # Set the number of records to display per page
    ordering = ['shift_start']  # Specify the field to sort on
    history_list_display = ["changed_fields","list_changes"]

    def show_history_link(self, obj):
        url = reverse('admin:{}_{}_history'.format(obj._meta.app_label, obj._meta.model_name), args=[obj.pk])
        return format_html('<a href="{}">History</a>', url)
    show_history_link.short_description = 'History'

    def changed_fields(self, obj):
        if obj.prev_record:
            delta = obj.diff_against(obj.prev_record)
            return delta.changed_fields
        return None

admin.site.register(Utilization,Utilization_ModelAdmin)

class Utilization_FileUploadAdmin(admin.ModelAdmin):
    list_display = ['id','file', 'upload_timestamp']  # Specify the fields to display in the table
    list_per_page = 20  # Set the number of records to display per page

    readonly_fields = ['upload_timestamp']

    def save_model(self, request, obj, form, change):
        obj.save(request=request)

admin.site.register(Utilization_FileUpload, Utilization_FileUploadAdmin)


class Quality_ModelAdmin(SimpleHistoryAdmin, admin.ModelAdmin):

    search_fields = ['id_metrics_master','metric_value', 'region']
    list_display = ['id_metrics_master','metric_value', 'region','id_country','id_period','id_calendar_period','id_datastream','id_audit','show_history_link']  # Specify the fields to display in the table
    list_per_page = 700  # Set the number of records to display per page
    ordering = ['id_calendar_period']  # Specify the field to sort on
    history_list_display = ["changed_fields","list_changes"]

    def show_history_link(self, obj):
        url = reverse('admin:{}_{}_history'.format(obj._meta.app_label, obj._meta.model_name), args=[obj.pk])
        return format_html('<a href="{}">History</a>', url)
    show_history_link.short_description = 'History'

    def changed_fields(self, obj):
        if obj.prev_record:
            delta = obj.diff_against(obj.prev_record)
            return delta.changed_fields
        return None

admin.site.register(Quality,Quality_ModelAdmin)

class Quality_FileUploadAdmin(admin.ModelAdmin):
    list_display = ['id','file', 'upload_timestamp']  # Specify the fields to display in the table
    list_per_page = 20  # Set the number of records to display per page

    readonly_fields = ['upload_timestamp']

    def save_model(self, request, obj, form, change):
        obj.save(request=request)

admin.site.register(Quality_FileUpload, Quality_FileUploadAdmin)


class Service_Delivery_ModelAdmin(SimpleHistoryAdmin, admin.ModelAdmin):

    search_fields = ['country','bu_code','region', 'data_period']
    list_display = ['country','bu_code', 'region','frequency', 'data_period', 'processing_period', 'client_name', 'planned_db_availability_date',
            'actual_db_availability_date', 'planned_completion_date','actual_completion_date', 'delivery_days', 'ontime_late','late_delivery_reason','show_history_link']  # Specify the fields to display in the table
    
    list_per_page = 700  # Set the number of records to display per page
    # ordering = ['id_calendar_period']  # Specify the field to sort on
    history_list_display = ["changed_fields","list_changes"]

    def show_history_link(self, obj):
        url = reverse('admin:{}_{}_history'.format(obj._meta.app_label, obj._meta.model_name), args=[obj.pk])
        return format_html('<a href="{}">History</a>', url)
    show_history_link.short_description = 'History'

    def changed_fields(self, obj):
        if obj.prev_record:
            delta = obj.diff_against(obj.prev_record)
            return delta.changed_fields
        return None

admin.site.register(Service_Delivery,Service_Delivery_ModelAdmin)

class Service_Delivery_FileUploadAdmin(admin.ModelAdmin):
    list_display = ['id','file', 'upload_timestamp']  # Specify the fields to display in the table
    list_per_page = 20  # Set the number of records to display per page

    readonly_fields = ['upload_timestamp']

    def save_model(self, request, obj, form, change):
        obj.save(request=request)

admin.site.register(Service_Delivery_FileUpload, Service_Delivery_FileUploadAdmin)



class Productivity_ModelAdmin(SimpleHistoryAdmin, admin.ModelAdmin):

    search_fields = [ 'year','month', 'region','country', 'function']
    list_display = [
            'year','month', 'region','country', 'function', 'audit', 'employee_id', 'name', 'team_name', 'team_lead',
            'manager','tasks','target_prod_rate_hour','actual_prod_rate_hr',
            'productivity','stretch_target','task_processed','hour_spent_task',
            'hour_worked_sprout','overtime_approved','extended_work_hours',
            'fte_needed','fte_needed_target_sprout','fte_allocation'
        ]
    
    list_per_page = 700  # Set the number of records to display per page
    # ordering = ['id_calendar_period']  # Specify the field to sort on
    history_list_display = ["changed_fields","list_changes"]

    def show_history_link(self, obj):
        url = reverse('admin:{}_{}_history'.format(obj._meta.app_label, obj._meta.model_name), args=[obj.pk])
        return format_html('<a href="{}">History</a>', url)
    show_history_link.short_description = 'History'

    def changed_fields(self, obj):
        if obj.prev_record:
            delta = obj.diff_against(obj.prev_record)
            return delta.changed_fields
        return None

admin.site.register(Productivity,Productivity_ModelAdmin)

class Productivity_FileUploadAdmin(admin.ModelAdmin):
    list_display = ['id','file', 'upload_timestamp']  # Specify the fields to display in the table
    list_per_page = 20  # Set the number of records to display per page

    readonly_fields = ['upload_timestamp']

    def save_model(self, request, obj, form, change):
        obj.save(request=request)

admin.site.register(Productivity_FileUpload, Productivity_FileUploadAdmin)



class Rax_Utilization_ModelAdmin(SimpleHistoryAdmin, admin.ModelAdmin):

    search_fields = ['quarter', 'region', 'name', 'team', 'month', 'manager']
    list_display = [ 'quarter', 'region', 'name', 'team', 'month', 'manager','active', 'idle', 'shrinkage', 'show_history_link']  # Specify the fields to display in the table
    
    list_per_page = 700  # Set the number of records to display per page
    # ordering = ['id_calendar_period']  # Specify the field to sort on
    history_list_display = ["changed_fields","list_changes"]

    def show_history_link(self, obj):
        url = reverse('admin:{}_{}_history'.format(obj._meta.app_label, obj._meta.model_name), args=[obj.pk])
        return format_html('<a href="{}">History</a>', url)
    show_history_link.short_description = 'History'

    def changed_fields(self, obj):
        if obj.prev_record:
            delta = obj.diff_against(obj.prev_record)
            return delta.changed_fields
        return None

admin.site.register(Rax_Utilization,Rax_Utilization_ModelAdmin)

class Rax_Utilization_FileUploadAdmin(admin.ModelAdmin):
    list_display = ['id','file', 'upload_timestamp']  # Specify the fields to display in the table
    list_per_page = 20  # Set the number of records to display per page

    readonly_fields = ['upload_timestamp']

    def save_model(self, request, obj, form, change):
        obj.save(request=request)

admin.site.register(Rax_Utilization_FileUpload, Rax_Utilization_FileUploadAdmin)


class Quality_Report_ModelAdmin(SimpleHistoryAdmin, admin.ModelAdmin):
 
    search_fields = ['region','country', 'team', 'month']
    list_display = ['region','country', 'data_source','team', 'data_stream', 'frequency', 'audit', 'month', 'checked', 'errors', 'accuracy', 'show_history_link']  # Specify the fields to display in the table
    list_per_page = 700  # Set the number of records to display per page
    ordering = ['region']  # Specify the field to sort on
    history_list_display = ["changed_fields","list_changes"]

    def show_history_link(self, obj):
        url = reverse('admin:{}_{}_history'.format(obj._meta.app_label, obj._meta.model_name), args=[obj.pk])
        return format_html('<a href="{}">History</a>', url)
    show_history_link.short_description = 'History'

    def changed_fields(self, obj):
        if obj.prev_record:
            delta = obj.diff_against(obj.prev_record)
            return delta.changed_fields
        return None

admin.site.register(Quality_Report,Quality_Report_ModelAdmin)

class Quality_Report_FileUploadAdmin(admin.ModelAdmin):
    list_display = ['id','file', 'upload_timestamp']  # Specify the fields to display in the table
    list_per_page = 20  # Set the number of records to display per page

    readonly_fields = ['upload_timestamp']

    def save_model(self, request, obj, form, change):
        obj.save(request=request)

admin.site.register(Quality_Report_FileUpload, Quality_Report_FileUploadAdmin)


class Attrition_ModelAdmin(SimpleHistoryAdmin, admin.ModelAdmin):

    search_fields = [ 'manager','analyst_name', 'audit_stream','team_lead', 'team','emp_id']
    list_display = [
            'department','team','team_lead','manager','emp_id','analyst_name','date_hired','resignation_eff_date','audit_stream','reason'
        ]
    
    list_per_page = 700  # Set the number of records to display per page
    # ordering = ['id_calendar_period']  # Specify the field to sort on
    history_list_display = ["changed_fields","list_changes"]

    def show_history_link(self, obj):
        url = reverse('admin:{}_{}_history'.format(obj._meta.app_label, obj._meta.model_name), args=[obj.pk])
        return format_html('<a href="{}">History</a>', url)
    show_history_link.short_description = 'History'

    def changed_fields(self, obj):
        if obj.prev_record:
            delta = obj.diff_against(obj.prev_record)
            return delta.changed_fields
        return None

admin.site.register(Attrition,Attrition_ModelAdmin)

class Attrition_FileUploadAdmin(admin.ModelAdmin):
    list_display = ['id','file', 'upload_timestamp']  # Specify the fields to display in the table
    list_per_page = 20  # Set the number of records to display per page

    readonly_fields = ['upload_timestamp']

    def save_model(self, request, obj, form, change):
        obj.save(request=request)

admin.site.register(AttritionListFileUpload, Attrition_FileUploadAdmin)









