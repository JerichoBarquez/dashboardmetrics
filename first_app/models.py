from django.db import models
from datetime import date
from django.db.models.signals import post_save
from django.dispatch import receiver
import pandas as pd
from django.db import transaction
from django.contrib import messages
from django.utils import timezone
from django.utils.text import slugify
from django.utils.timezone import make_aware
from pandas import isnull
import math
from pandas._libs.tslibs.nattype import NaTType
from simple_history.models import HistoricalRecords
import os
from datetime import timedelta, datetime
from django.db.models.query import QuerySet
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Q

 

    
# class Department(models.Model):
#     department = models.CharField(max_length=25)
    
#     def __str__(self):
#         return self.department

class Function(models.Model):
    function = models.CharField(max_length=50)
    
    def __str__(self):
        return self.function
    
# class Grade(models.Model):
#     grade = models.IntegerField()
    
#     def __str__(self):
#         return str(self.grade)
    
class CFunction(models.Model):
    c_function = models.CharField(max_length=50)
    
    def __str__(self):
        return self.c_function


# class Tier_5(models.Model):
#     tier_5 = models.CharField(max_length=50)
    
#     def __str__(self):
#         return self.tier_5
    
class MovementType(models.Model):
    movement_type = models.CharField(max_length=50)
    
    def __str__(self):
        return self.movement_type
    
# class Status(models.Model):
#     status = models.CharField(max_length=25)
    
#     def __str__(self):
#         return self.status
    
class Reason(models.Model):
    reason = models.CharField(max_length=100)

    def __str__(self):
        return self.reason
    
    
    
class MasterList(models.Model):
    emp_id = models.IntegerField(unique=True)
    firstname = models.CharField(max_length=50,null=True, blank=True)
    lastname = models.CharField(max_length=50,null=True, blank=True)
    hire_date = models.DateField(default=date.today)
    position = models.CharField(max_length=50,null=True, blank=True)
    job_title = models.CharField(max_length=50,null=True, blank=True)
    job_profile = models.CharField(max_length=50,null=True, blank=True)
    grade_profile_id = models.CharField(max_length=50,null=True, blank=True)
    grade = models.IntegerField(null=True, blank=True)
    grade_profile_id = models.CharField(max_length=100,null=True, blank=True)
    # emp_status = models.ForeignKey(Status, on_delete=models.CASCADE, null=True, blank=True)
    job_family = models.CharField(max_length=50,null=True, blank=True)
    job_family_group = models.CharField(max_length=50,null=True, blank=True)
    worker_type = models.CharField(max_length=25,null=True, blank=True)
    full_Part = models.CharField(max_length=25,null=True, blank=True)
    scheduled_std_hours = models.IntegerField(null=True)
    cost_center_id = models.CharField(max_length=50,null=True, blank=True)
    cost_center_name = models.CharField(max_length=50,null=True, blank=True)
    profit_center = models.CharField(max_length=50,null=True, blank=True)
    worker_business_unit = models.CharField(max_length=50,null=True, blank=True)
    location_code = models.CharField(max_length=50,null=True, blank=True)
    location = models.CharField(max_length=50,null=True, blank=True)
    city = models.CharField(max_length=50,null=True, blank=True)
    state = models.CharField(max_length=50,null=True, blank=True)
    country_name = models.CharField(max_length=50,null=True, blank=True)
    geo_region = models.CharField(max_length=50,null=True, blank=True)
    sub_region = models.CharField(max_length=50,null=True, blank=True)
    no_of_directs = models.CharField(max_length=50,null=True, blank=True)
    manager_id = models.IntegerField(null=True, blank=True)
    manager_name = models.CharField(max_length=100,null=True, blank=True)
    tier_1 = models.CharField(max_length=100,null=True, blank=True) 
    tier_2 = models.CharField(max_length=100,null=True, blank=True) 
    tier_3 = models.CharField(max_length=100,null=True, blank=True) 
    tier_4 = models.CharField(max_length=100,null=True, blank=True) 
    tier_5 = models.CharField(max_length=100,null=True, blank=True) 
    tier_6 = models.CharField(max_length=100,null=True, blank=True) 
    tier_7 = models.CharField(max_length=100,null=True, blank=True) 
    region = models.CharField(max_length=100,null=True, blank=True) 

    history = HistoricalRecords()

    def __str__(self):
        return str(self.emp_id)
    


class Attrition(models.Model):
    
    department = models.CharField(max_length=50,null=True, blank=True)
    team = models.CharField(max_length=50,null=True, blank=True)
    team_lead = models.CharField(max_length=100,null=True, blank=True)
    manager = models.CharField(max_length=100,null=True, blank=True)
    emp_id = models.CharField(max_length=50,null=True, blank=True)
    analyst_name = models.CharField(max_length=100,null=True, blank=True)
    date_hired = models.DateField(default=date.today,null=True, blank=True)
    resignation_eff_date = models.DateField(default=date.today,null=True, blank=True)
    audit_stream = models.CharField(max_length=50,null=True, blank=True)
    reason = models.CharField(max_length=250,null=True, blank=True)
    comment = models.CharField(max_length=250,null=True, blank=True)
    
    history = HistoricalRecords()
    
    def __str__(self):
        return str(self.emp_id)
    

class AttritionListFileUpload(models.Model):
    file = models.FileField(upload_to='attrition', null=True, blank=True)
    upload_timestamp = models.DateTimeField(default=timezone.now)

    def insert_records_to_attrition_list(self):
        file_path = self.file.path

        # Read the Excel file
        excel_file = pd.ExcelFile(file_path)

        
        required_sheets = {'Attrition - USCA', 'Attrition - EMEA', 'Attrition - APAC'}
        sheet_names = [sheet for sheet in excel_file.sheet_names if sheet in required_sheets]
        
        missing_sheets = required_sheets - set(sheet_names)
        if missing_sheets:
            print(f"Missing sheets in the uploaded file: {missing_sheets}")
        # Initialize counter
        total_inserted_count = 0

        # Loop through each sheet
        for sheet_name in sheet_names:
            # Read the Excel file for the current sheet
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            print(f"Processing sheet: {sheet_name}")
            print(f"Columns in sheet '{sheet_name}': {df.columns.tolist()}")
            
            if df.empty:
                print(f"Skipping empty sheet: {sheet_name}")
                continue
    

            # Column mapping and renaming (your existing code)
            column_mapping = {
            'Department': 'department',
            'Team': 'team',
            'Team Lead': 'team_lead',
            'Manager': 'manager',
            'Employee ID': 'emp_id',
            'Analyst Name': 'analyst_name',
            'Date Hired': 'date_hired',
            'Resignation Effectivity Date': 'resignation_eff_date',
            'Audit/Stream': 'audit_stream',
            'Reason': 'reason',
            'Comment (Other Reasons)': 'comment',

            }

            df.rename(columns=column_mapping, inplace=True)
            
            # Extract the required columns from the DataFrame
            columns = [
                'department', 'team', 'team_lead', 'manager', 'emp_id', 'analyst_name', 'date_hired', 'resignation_eff_date', 'audit_stream', 'reason', 'comment'
            ]
            df = df[columns].dropna(how='all')
            
         

            # Convert DataFrame to list of dictionaries
            records = df.to_dict('records')
            

            # Clean up string columns
            for record in records:
                for column in ['department', 'team', 'team_lead', 'manager', 'emp_id', 'analyst_name','audit_stream']:
                    if isinstance(record[column], str):
                        record[column] = record[column].strip()

            # Initialize counter for the current sheet
            inserted_count = 0

            # Bulk insert the records for the current sheet
            # with transaction.atomic():
            #     for record in records:
            #         Attrition.objects.create(**record)
            #         inserted_count += 1
            
            with transaction.atomic():             
                    attrition_objects = [Attrition(**record) for record in records]
                    Attrition.objects.bulk_create(attrition_objects)
                   

            inserted_count = len(attrition_objects)

            print(f"Sheet '{sheet_name}': {inserted_count} records inserted.")
            total_inserted_count += inserted_count

        return total_inserted_count

    def save(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().save(*args, **kwargs)
        if request is not None:
            inserted_count = self.insert_records_to_attrition_list()
          
            if inserted_count > 0:
                message = f"{inserted_count} records were inserted."
                messages.success(request, message)
    

class MasterListFileUpload(models.Model):
    file = models.FileField(upload_to='master_list_files', null=True, blank=True)
    upload_timestamp = models.DateTimeField(default=timezone.now)

    def insert_records_to_master_list(self):
        file_path = self.file.path

        # Read the Excel file
        df = pd.read_excel(file_path, sheet_name="Data")
        print(df)

        # Clean the column names by stripping leading and trailing spaces
        df.columns = df.columns.str.strip()

        # Get the index of the 'Last,First Name' column
        column_index = df.columns.get_loc('Last,First Name')

        # Create new columns 'Lastname' and 'Firstname' by splitting the column
        df[['Lastname', 'Firstname']] = df.iloc[:, column_index].str.split(',', n=1, expand=True)

        # Map the Excel column names to the corresponding fields in the model
        column_mapping = {
            'Employee ID': 'emp_id',
            'Firstname': 'firstname',
            'Lastname': 'lastname',
            'Original Hire Date': 'hire_date',
            'Position': 'position',
            'Job Title': 'job_title',
            'Job Profile': 'job_profile',
            'Grade Profile ID': 'grade_profile_id',
            'Grade': 'grade',
            'Job Family': 'job_family',
            'Job Family Group': 'job_family_group',
            'Worker Type': 'worker_type',
            'Full/Part': 'full_Part',
            'Scheduled Std Hours - Calculated FTE': 'scheduled_std_hours',
            'Cost Center - ID': 'cost_center_id',
            'Cost Center - Name': 'cost_center_name',
            'Profit Center': 'profit_center',
            "Worker's Business Unit": 'worker_business_unit',
            'Location Code': 'location_code',
            'Location': 'location',
            'City': 'city',
            'State': 'state',
            'Country Name': 'country_name',
            'Geo Region': 'geo_region',
            'Sub Region': 'sub_region',
            'No. of Directs': 'no_of_directs',
            'Manager ID': 'manager_id',
            'Manager Name': 'manager_name',
            'Tier 1': 'tier_1',
            'Tier 2': 'tier_2',
            'Tier 3': 'tier_3',
            'Tier 4': 'tier_4',
            'Tier 5': 'tier_5',
            'Tier 6': 'tier_6',
            'Tier 7': 'tier_7',
            'Region': 'region',
        }

        # Rename the columns in the DataFrame based on the mapping
        df.rename(columns=column_mapping, inplace=True)

        # Extract the required columns from the DataFrame
        columns = [
            'emp_id', 'lastname', 'firstname', 'hire_date', 'position', 'job_title',
            'job_profile', 'grade_profile_id', 'grade', 'job_family', 'job_family_group',
            'worker_type', 'full_Part', 'scheduled_std_hours',
            'cost_center_id', 'cost_center_name', 'profit_center', 'worker_business_unit',
            'location_code', 'location', 'city', 'state', 'country_name', 'geo_region',
            'sub_region', 'no_of_directs', 'manager_id', 'manager_name', 'tier_1',
            'tier_2', 'tier_3', 'tier_4', 'tier_5', 'tier_6', 'tier_7', 'region',
        ]

        data = df[columns]

        # Convert DataFrame to list of dictionaries
        records = data.to_dict('records')

        inserted_count = 0
       
        MasterList.objects.all().delete()
        with transaction.atomic():
            for record in records:
                MasterList.objects.create(**record)  # Insert the new record
                inserted_count += 1
                
        # Return the count of inserted and duplicate records
        return inserted_count

    def save(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().save(*args, **kwargs)

        if request is not None:
            inserted_count = self.insert_records_to_master_list()
            message = f"{inserted_count} records were inserted."
            messages.success(request, message)





class Attendance(models.Model):
    att_date = models.DateField(default=date.today,null=True, blank=True)
    site = models.CharField(max_length=100,null=True, blank=True)
    prod_manager = models.CharField(max_length=100,null=True, blank=True)
    assoc_manager = models.CharField(max_length=100,null=True, blank=True)
    tlead = models.CharField(max_length=100,null=True, blank=True)
    team = models.CharField(max_length=100,null=True, blank=True)
    country = models.CharField(max_length=50,null=True, blank=True)
    region = models.CharField(max_length=25,null=True, blank=True)
    emp_id = models.CharField(max_length=100,null=True, blank=True)
    emp_name = models.CharField(max_length=100,null=True, blank=True)
    status = models.CharField(max_length=100,null=True, blank=True)
    type = models.CharField(max_length=50,null=True, blank=True)
    reason = models.CharField(max_length=250,null=True, blank=True)
    upload = models.CharField(max_length=100,null=True, blank=True)


    history = HistoricalRecords()
    
    def __str__(self):
        return self.emp_name
    

class Supervisor_APAC(models.Model):
     team_name = models.CharField(max_length=100,null=True, blank=True)
     production_manager = models.CharField(max_length=100,null=True, blank=True)
     associate_manager = models.CharField(max_length=100,null=True, blank=True)
     team_lead = models.CharField(max_length=100,null=True, blank=True)

     history = HistoricalRecords()

     def __str__(self):
        return self.team_name
     
class Supervisor_EMEA(models.Model):
     team_name = models.CharField(max_length=100,null=True, blank=True)
     production_manager = models.CharField(max_length=100,null=True, blank=True)
     associate_manager = models.CharField(max_length=100,null=True, blank=True)
     team_lead = models.CharField(max_length=100,null=True, blank=True)

     history = HistoricalRecords()

     def __str__(self):
        return self.team_name

class Supervisor_USCA(models.Model):
     team_name = models.CharField(max_length=100,null=True, blank=True)
     production_manager = models.CharField(max_length=100,null=True, blank=True)
     associate_manager = models.CharField(max_length=100,null=True, blank=True)
     team_lead = models.CharField(max_length=100,null=True, blank=True)

     history = HistoricalRecords()

     def __str__(self):
        return self.team_name
     
    

class Supervisor_emea_fileupload(models.Model):
    file = models.FileField(upload_to='emea_supervisor', null=True, blank=True)
    upload_timestamp = models.DateTimeField(default=timezone.now)

    def insert_records_to_master_list(self, sheet_name):
        file_path = self.file.path

        # Check if the specified sheet_name exists in the Excel file
        with pd.ExcelFile(file_path) as xls:
            if sheet_name not in xls.sheet_names:
                return 0  # Return 0 if the sheet doesn't exist

            # Read the Excel file from the specified sheet_name
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            print(df)
        
        column_mapping = {
            'Team': 'team_name',
            'PRODUCTION MANAGER': 'production_manager',
            'ASSOCIATE MANAGER': 'associate_manager',
            'TEAM LEADER': 'team_lead'
        }

        # Rename the columns in the DataFrame based on the mapping
        df.rename(columns=column_mapping, inplace=True)

        # Extract the required columns from the DataFrame
        columns = [
            'team_name', 'production_manager', 'associate_manager', 'team_lead'
        ]

        df = df[df['team_name'] != 'ALL']

        data = df[columns]

        # Convert DataFrame to list of dictionaries
        records = data.to_dict('records')

        # Initialize counters
        inserted_count = 0

        # Bulk insert the records
        with transaction.atomic():
            for record in records:
                Supervisor_EMEA.objects.create(**record)
                inserted_count += 1

        # Return the count of inserted records
        return inserted_count

    def save(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().save(*args, **kwargs)
        if request is not None:
            # Specify the sheet name you want to read data from (e.g., "Sheet 3")
            sheet_name = "Sheet3"
            
            inserted_count = self.insert_records_to_master_list(sheet_name)

            if isinstance(inserted_count, int) and inserted_count > 0:
                message = f"{inserted_count} records were inserted."
                messages.success(request, message)


class Supervisor_usca_fileupload(models.Model):
    file = models.FileField(upload_to='usca_supervisor', null=True, blank=True)
    upload_timestamp = models.DateTimeField(default=timezone.now)

    def insert_records_to_master_list(self, sheet_name):
        file_path = self.file.path

        # Check if the specified sheet_name exists in the Excel file
        with pd.ExcelFile(file_path) as xls:
            if sheet_name not in xls.sheet_names:
                return 0  # Return 0 if the sheet doesn't exist

            # Read the Excel file from the specified sheet_name
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            print(df)
        
        column_mapping = {
            'Team': 'team_name',
            'PRODUCTION MANAGER': 'production_manager',
            'ASSOCIATE MANAGER': 'associate_manager',
            'TEAM LEADER': 'team_lead'
        }

        # Rename the columns in the DataFrame based on the mapping
        df.rename(columns=column_mapping, inplace=True)

        # Extract the required columns from the DataFrame
        columns = [
            'team_name', 'production_manager', 'associate_manager', 'team_lead'
        ]

        df = df[df['team_name'] != 'ALL']

        data = df[columns]

        # Convert DataFrame to list of dictionaries
        records = data.to_dict('records')

        # Initialize counters
        inserted_count = 0

        # Bulk insert the records
        with transaction.atomic():
            for record in records:
                Supervisor_USCA.objects.create(**record)
                inserted_count += 1

        # Return the count of inserted records
        return inserted_count

    def save(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().save(*args, **kwargs)
        if request is not None:
            # Specify the sheet name you want to read data from (e.g., "Sheet 3")
            sheet_name = "Sheet3"
            
            inserted_count = self.insert_records_to_master_list(sheet_name)

            if isinstance(inserted_count, int) and inserted_count > 0:
                message = f"{inserted_count} records were inserted."
                messages.success(request, message)


    

class Attendance_FileUpload(models.Model):
    file = models.FileField(upload_to='attendance', null=True, blank=True)
    upload_timestamp = models.DateTimeField(default=timezone.now)

    def insert_records_to_master_list(self, sheet_name):
        file_path = self.file.path

        # Read the Excel file
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        column_mapping = {
            'Date': 'att_date',
            'Site': 'site',
            'Team': 'team',
            'Country': 'country',
            'Group': 'region',
            'EmpID': 'emp_id',
            'Name': 'emp_name',
            'Status': 'status',
            'Type': 'type',
            'Reason': 'reason',
            'Upload': 'upload',
        }

        # Rename the columns in the DataFrame based on the mapping
        df.rename(columns=column_mapping, inplace=True)
        df['att_date'] = pd.to_datetime(df['att_date'], format='%m/%d/%Y').dt.strftime('%Y-%m-%d')
        

        # Extract the required columns from the DataFrame
        columns = [
            'att_date', 'site', 'team', 'country', 'region', 'emp_id',
            'emp_name', 'status', 'type', 'reason', 'upload'
        ]


        data = df[columns]

        # Convert DataFrame to list of dictionaries
        records = data.to_dict('records')
        
        
       # Initialize counters
        inserted_count = 0

        # Retrieve existing dates from the table and convert to list
        existing_dates = list(Attendance.objects.values_list('att_date', flat=True))

        # Convert existing dates to datetime.date objects
        existing_dates = [date if date is not None else None for date in existing_dates]

        # Convert record dates to datetime.date objects
        record_dates = [
            datetime.strptime(str(record['att_date']), '%Y-%m-%d').date()
            if record['att_date'] is not None and str(record['att_date']) != 'nan'  and str(record['att_date'].lower()) != 'nan'
            else None
            for record in records
        ]

        # Bulk insert the records
        with transaction.atomic():
            for record in records:
                if 'att_date' in record and (isinstance(record['att_date'], float) or isinstance(record['att_date'], pd._libs.tslibs.nattype.NaTType)):
                    record['att_date'] = None
                
                # Convert emp_id to string
                if 'emp_id' in record:
                    record['emp_id'] = str(record['emp_id']).split('.')[0]
                
                # Get the corresponding Team_Supervisor_APAC record
                team_supervisor_apac = Supervisor_APAC.objects.filter(team_name=record['team']).first()
                if team_supervisor_apac:
                    # Populate the fields with data from Team_Supervisor_APAC
                    record['prod_manager'] = team_supervisor_apac.production_manager
                    record['assoc_manager'] = team_supervisor_apac.associate_manager
                    record['tlead'] = team_supervisor_apac.team_lead
                
                team_supervisor_emea = Supervisor_EMEA.objects.filter(team_name=record['team']).first()
                if team_supervisor_emea:
                    # Populate the fields with data from Team_Supervisor_APAC
                    record['prod_manager'] = team_supervisor_emea.production_manager
                    record['assoc_manager'] = team_supervisor_emea.associate_manager
                    record['tlead'] = team_supervisor_emea.team_lead
                
                team_supervisor_usca = Supervisor_USCA.objects.filter(team_name=record['team']).first()
                if team_supervisor_usca:
                    record['prod_manager'] = team_supervisor_usca.production_manager
                    record['assoc_manager'] = team_supervisor_usca.associate_manager
                    record['tlead'] = team_supervisor_usca.team_lead

                Attendance.objects.create(**record)
                inserted_count += 1
                
        # Return the count of inserted
        return inserted_count

    def save(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().save(*args, **kwargs)
        if request is not None:
            with pd.ExcelFile(self.file.path) as xls:
                for sheet_name in xls.sheet_names:
                    inserted_count = self.insert_records_to_master_list(sheet_name)
                    # if isinstance(inserted_count, list) and len(inserted_count) > 0:
                    #     message = "Check your record " + f"{inserted_count}. Similar dates has been uploaded already. Avoid uploading similar dates to maintain accuracy of Attendance!"
                    #     messages.warning(request, message)
                    #     self.delete()
                    if isinstance(inserted_count, int) and inserted_count > 0:
                        message = f"{inserted_count} records were inserted."
                        messages.success(request, message)
    # def delete(self, *args, **kwargs):
    #     self.file.delete(save=False)  # Delete the file from the file system
    #     super().delete(*args, **kwargs)  # Call the superclass delete method to remove the instance from the database



class Utilization(models.Model):
    emp_id = models.CharField(max_length=100,null=True, blank=True)
    region = models.CharField(max_length=100,null=True, blank=True)
    user = models.CharField(max_length=100,null=True, blank=True)
    name = models.CharField(max_length=100,null=True, blank=True)
    team = models.CharField(max_length=250,null=True, blank=True)
    country = models.CharField(max_length=250,null=True, blank=True)
    subtask = models.CharField(max_length=100,null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    time_spent_in_min = models.CharField(max_length=100,null=True, blank=True)
    shift_start = models.DateTimeField(null=True, blank=True)
    week = models.CharField(max_length=100,null=True, blank=True)
    duration_hour = models.CharField(max_length=100,null=True, blank=True)
    team_rax = models.CharField(max_length=250,null=True, blank=True)

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.region} - {self.team}"

    
class Utilization_FileUpload(models.Model):
    file = models.FileField(upload_to='utilization', null=True, blank=True)
    upload_timestamp = models.DateTimeField(default=timezone.now)

    def insert_records_to_master_list(self):
        file_path = self.file.path

        # Read the Excel file
        excel_file = pd.ExcelFile(file_path)

        # Get sheet names dynamically
        sheet_names = excel_file.sheet_names

        # Initialize counter
        total_inserted_count = 0

        # Loop through each sheet
        for sheet_name in sheet_names:
            # Read the Excel file for the current sheet
            df = pd.read_excel(excel_file, sheet_name=sheet_name)

            # Column mapping and renaming (your existing code)
            column_mapping = {
            'Region': 'region',
            'User': 'user',
            'Name': 'name',
            'Team Name': 'team',
            'SubTask': 'subtask',
            'Quantity': 'quantity',
            'Time spent in Min': 'time_spent_in_min',
            'Shift Start': 'shift_start',
            'Duration in HR': 'duration_hour',
            'Week': 'week',
            'EID': 'emp_id',
            'Team RAX': 'team_rax',
            'Country': 'country'
            }

            df.rename(columns=column_mapping, inplace=True)

            # Extract the required columns from the DataFrame
            columns = [
                'region', 'user', 'name', 'team', 'subtask', 'quantity', 'time_spent_in_min',
                'shift_start', 'duration_hour', 'week', 'emp_id', 'team_rax', 'country'
            ]
            data = df[columns]

            # Convert DataFrame to list of dictionaries
            records = data.to_dict('records')

            # Clean up string columns
            for record in records:
                for column in ['region', 'user', 'name', 'team', 'subtask', 'country']:
                    if isinstance(record[column], str):
                        record[column] = record[column].strip()

            # Initialize counter for the current sheet
            inserted_count = 0

            # Bulk insert the records for the current sheet
            with transaction.atomic():
                for record in records:
                    Utilization.objects.create(**record)
                    inserted_count += 1

            # Add the count for the current sheet to the total count
            total_inserted_count += inserted_count

        # Return the total count of inserted records
        return total_inserted_count

    def save(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().save(*args, **kwargs)
        if request is not None:
            inserted_count = self.insert_records_to_master_list()
          
            if inserted_count > 0:
                message = f"{inserted_count} records were inserted."
                messages.success(request, message)


class Quality(models.Model):
    id_metrics_master = models.CharField(max_length=250,null=True, blank=True)
    metric_value = models.CharField(max_length=100,null=True, blank=True)
    region = models.CharField(max_length=100,null=True, blank=True)
    id_country = models.CharField(max_length=100,null=True, blank=True)
    id_period = models.CharField(max_length=100,null=True, blank=True)
    id_calendar_period = models.CharField(max_length=100,null=True, blank=True)
    id_datastream = models.CharField(max_length=100,null=True, blank=True)
    id_audit = models.CharField(max_length=100,null=True, blank=True)

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.id_metrics_master} - {self.region}"
    

class Quality_FileUpload(models.Model):
    file = models.FileField(upload_to='quality', null=True, blank=True)
    upload_timestamp = models.DateTimeField(default=timezone.now)

    def insert_records_to_master_list(self):
        file_path = self.file.path
        sheet_name = "KPI"
        # Read the Excel file
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        column_mapping = {
            'Id_Metrics_Master': 'id_metrics_master',
            'Metric_Value': 'metric_value',
            'Region': 'region',
            'id_country': 'id_country',
            'id_Period': 'id_period',
            'id_calendar_Period': 'id_calendar_period',
            'Id_Datastream': 'id_datastream',
            'Id_Audit': 'id_audit'
        }

        # Rename the columns in the DataFrame based on the mapping
        df.rename(columns=column_mapping, inplace=True)
        
        # Extract the required columns from the DataFrame
        columns = [
            'id_metrics_master','metric_value', 'region', 'id_country', 'id_period', 'id_calendar_period', 'id_datastream',
            'id_audit'
        ]

        data = df[columns]

        # Convert DataFrame to list of dictionaries
        records = data.to_dict('records')

        for record in records:
            for column in ['id_metrics_master', 'metric_value', 'region', 'id_country', 'id_period','id_calendar_period','id_datastream','id_audit']:
                if isinstance(record[column], str):
                    record[column] = record[column].strip()
        
       # Initialize counters
        inserted_count = 0

        # Bulk insert the records
        with transaction.atomic():
            for record in records:
                
                Quality.objects.create(**record)
                inserted_count += 1
                
        # Return the count of inserted
        return inserted_count

    def save(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().save(*args, **kwargs)
        if request is not None:
            inserted_count = self.insert_records_to_master_list()
          
            if inserted_count > 0:
                message = f"{inserted_count} records were inserted."
                messages.success(request, message)



class Service_Delivery(models.Model):
    country = models.CharField(max_length=50,null=True, blank=True)
    bu_code = models.CharField(max_length=50,null=True, blank=True)
    region = models.CharField(max_length=25,null=True, blank=True)
    audit = models.CharField(max_length=250,null=True, blank=True)
    audit_type = models.CharField(max_length=100,null=True, blank=True)
    frequency = models.CharField(max_length=50,null=True, blank=True)
    data_period = models.CharField(max_length=100,null=True, blank=True)
    processing_period = models.CharField(max_length=50,null=True, blank=True)
    customer_code = models.CharField(max_length=50,null=True, blank=True)
    client_name = models.CharField(max_length=250,null=True, blank=True)
    report_output_name = models.CharField(max_length=250,null=True, blank=True)
    output_type = models.CharField(max_length=50,null=True, blank=True)
    final_output_format = models.CharField(max_length=100,null=True, blank=True)
    planned_db_availability_date = models.CharField(max_length=50,null=True, blank=True)
    actual_db_availability_date = models.CharField(max_length=50,null=True, blank=True)
    planned_completion_date = models.CharField(max_length=50,null=True, blank=True)
    actual_completion_date = models.CharField(max_length=50,null=True, blank=True)
    delivery_days = models.CharField(max_length=25,null=True, blank=True)
    ontime_late = models.CharField(max_length=25,null=True, blank=True)
    late_delivery_reason = models.CharField(max_length=250,null=True, blank=True)
    count_of_rework = models.CharField(max_length=25,null=True, blank=True)
    count_of_reissue = models.CharField(max_length=25,null=True, blank=True)
    dispatch_mode = models.CharField(max_length=50,null=True, blank=True)
    data_source = models.CharField(max_length=50,null=True, blank=True)
    data_source_type = models.CharField(max_length=50,null=True, blank=True)
    
    
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.country} - {self.bu_code}"
    


class Service_Delivery_FileUpload(models.Model):
    file = models.FileField(upload_to='service_delivery', null=True, blank=True)
    upload_timestamp = models.DateTimeField(default=timezone.now)

    def insert_records_to_master_list(self):
        file_path = self.file.path
        sheet_name = "UPM Deliveries"
        # Read the Excel file
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        column_mapping = {
            'COUNTRY': 'country',
            'BU_CODE': 'bu_code',
            'REGION': 'region',
            'AUDIT': 'audit',
            'AUDIT_TYPE': 'audit_type',
            'FREQUENCY': 'frequency',
            'DATA_PERIOD': 'data_period',
            'PROCESSING_PERIOD': 'processing_period',
            'CLIENT_NAME': 'client_name',
            'REPORT_OUTPUT_NAME': 'report_output_name',
            'OUTPUT_TYPE': 'output_type',
            'FINAL_OUTPUT_FORMAT': 'final_output_format',
            'PLANNED_DB_AVAILABILITY_DATE': 'planned_db_availability_date',
            'ACTUAL_DB_AVAILABILITY_DATE': 'actual_db_availability_date',
            'PLANNED_COMPLETION_DATE': 'planned_completion_date',
            'ACTUAL_COMPLETION_DATE': 'actual_completion_date',
            'DELIVERY_DAYS': 'delivery_days',
            'ONTIME/LATE': 'ontime_late',
            'LATE_DELIVERY_REASON': 'late_delivery_reason',
            'COUNT_OF_REWORK': 'count_of_rework',
            'COUNT_OF_REISSUE': 'count_of_reissue',
            'DISPATCH_MODE': 'dispatch_mode',
            'DATA_SOURCE': 'data_source',
            'DATA_SOURCE_TYPE': 'data_source_type'
        }


        # Rename the columns in the DataFrame based on the mapping
        df.rename(columns=column_mapping, inplace=True)
        
        # Extract the required columns from the DataFrame
        columns = [
            'country','bu_code', 'region','frequency', 'data_period', 'processing_period', 'client_name', 'planned_db_availability_date',
            'actual_db_availability_date', 'planned_completion_date','actual_completion_date', 'delivery_days', 'ontime_late','late_delivery_reason',
        ]

        data = df[columns]

        # Convert DataFrame to list of dictionaries
        records = data.to_dict('records')

        for record in records:
            for column in ['country', 'bu_code','region', 'frequency', 'data_period', 'processing_period','client_name','planned_db_availability_date','ontime_late','delivery_days']:
                if isinstance(record[column], str):
                    record[column] = record[column].strip()
        
       # Initialize counters
        inserted_count = 0

        # Bulk insert the records
        with transaction.atomic():
            for record in records:
                
                Service_Delivery.objects.create(**record)
                inserted_count += 1
                
        # Return the count of inserted
        return inserted_count

    def save(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().save(*args, **kwargs)
        if request is not None:
            inserted_count = self.insert_records_to_master_list()
          
            if inserted_count > 0:
                message = f"{inserted_count} records were inserted."
                messages.success(request, message)
    

class Productivity(models.Model):
    year = models.CharField(max_length=10,null=True, blank=True)
    month = models.CharField(max_length=25,null=True, blank=True)
    region = models.CharField(max_length=10,null=True, blank=True)
    country = models.CharField(max_length=25,null=True, blank=True)
    function = models.CharField(max_length=50,null=True, blank=True)
    audit = models.CharField(max_length=100,null=True, blank=True)
    employee_id = models.CharField(max_length=25,null=True, blank=True)
    name = models.CharField(max_length=50,null=True, blank=True)
    team_name = models.CharField(max_length=50,null=True, blank=True)
    team_lead = models.CharField(max_length=50,null=True, blank=True)
    manager = models.CharField(max_length=50,null=True, blank=True)
    tasks = models.CharField(max_length=100,null=True, blank=True)
    target_prod_rate_hour = models.CharField(max_length=25,null=True, blank=True) # Need to change the column name. Chances that this column will change in 2025
    actual_prod_rate_hr = models.CharField(max_length=25,null=True, blank=True)
    productivity = models.CharField(max_length=100,null=True, blank=True)
    stretch_target = models.CharField(max_length=25,null=True, blank=True)
    task_processed = models.CharField(max_length=25,null=True, blank=True)
    hour_spent_task = models.CharField(max_length=25,null=True, blank=True)
    hour_worked_sprout = models.CharField(max_length=25,null=True, blank=True)
    overtime_approved = models.CharField(max_length=25,null=True, blank=True)
    extended_work_hours = models.CharField(max_length=25,null=True, blank=True)
    fte_needed = models.CharField(max_length=25,null=True, blank=True)
    fte_needed_target_sprout = models.CharField(max_length=25,null=True, blank=True)
    fte_allocation = models.CharField(max_length=25,null=True, blank=True)


    history = HistoricalRecords()

    def __str__(self):
        return f"{self.year} - {self.month}"
    
class Productivity_FileUpload(models.Model):
    file = models.FileField(upload_to='productivity', null=True, blank=True)
    upload_timestamp = models.DateTimeField(default=timezone.now)

    def insert_records_to_productivity(self):
        file_path = self.file.path
        sheet_name = "raw data"
        # Read the Excel file
   
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        column_mapping = {
            'Year': 'year',
            'Month': 'month',
            'Region': 'region',
            'Country': 'country',
            'Function': 'function',
            'Audit': 'audit',
            'Employee ID': 'employee_id',
            'Name': 'name',
            'Team Name': 'team_name',
            'Teamlead': 'team_lead',
            'Manager': 'manager',
            'Tasks': 'tasks',
            '2024 Target Prod Rate/Hour': 'target_prod_rate_hour',
            'Actual Prod Rate/Hour': 'actual_prod_rate_hr',
            'Productivity': 'productivity',
            'Stretch Target Prod Rate/Hour': 'stretch_target',
            'Volume/ Task Processed': 'task_processed',
            'Hours Spent (Task)': 'hour_spent_task',
            'Hours Worked (Sprout)': 'hour_worked_sprout',
            'Overtime (Approved)': 'overtime_approved',
            'Extended Working Hours': 'extended_work_hours',
            'FTE Needed (Sprout)': 'fte_needed', # changed the format of the column name from FTE Needed (Enter) (Sprout) to FTE Needed (Sprout)
            'FTE Needed (Stretch Traget/Sprout)': 'fte_needed_target_sprout',
            'FTE Allocation':'fte_allocation'
            
        }
        # Rename the columns in the DataFrame based on the mapping
        df.rename(columns=column_mapping, inplace=True)
        
        # Extract the required columns from the DataFrame
        columns = [
            'year','month', 'region','country', 'function', 'audit', 'employee_id', 'name', 'team_name', 'team_lead',
            'manager','tasks','target_prod_rate_hour','actual_prod_rate_hr',
            'productivity','stretch_target','task_processed','hour_spent_task',
            'hour_worked_sprout','overtime_approved','extended_work_hours',
            'fte_needed','fte_needed_target_sprout','fte_allocation'
        ]

        data = df[columns]

        # Convert DataFrame to list of dictionaries
        records = data.to_dict('records')

        # for record in records:
        #     for column in ['city_iso_code', 'team','period', 'region', 'country', 'hours','volumes','productivity']:
        #         if isinstance(record[column], str):
        #             record[column] = record[column].strip()
        
       # Initialize counters
        inserted_count = 0

        # Bulk insert the records
        with transaction.atomic():
            for record in records:
                
                Productivity.objects.create(**record)
                inserted_count += 1
                
        # Return the count of inserted
        return inserted_count

    def save(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().save(*args, **kwargs)
        if request is not None:
            inserted_count = self.insert_records_to_productivity()
          
            if inserted_count > 0:
                message = f"{inserted_count} records were inserted."
                messages.success(request, message)


class Rax_Utilization(models.Model):
    quarter = models.CharField(max_length=25,null=True, blank=True)
    region = models.CharField(max_length=50,null=True, blank=True)
    team = models.CharField(max_length=100,null=True, blank=True)
    manager = models.CharField(max_length=100,null=True, blank=True)
    month = models.CharField(max_length=25,null=True, blank=True)
    date = models.CharField(max_length=50,null=True, blank=True)
    eid = models.CharField(max_length=50,null=True, blank=True)
    name = models.CharField(max_length=150,null=True, blank=True)
    active = models.CharField(max_length=100,null=True, blank=True)
    idle = models.CharField(max_length=100,null=True, blank=True)
    shrinkage = models.CharField(max_length=100,null=True, blank=True)
    c_active = models.CharField(max_length=100,null=True, blank=True)
    c_idle = models.CharField(max_length=100,null=True, blank=True)
    overtime = models.CharField(max_length=100,null=True, blank=True)
    c_shrinkages = models.CharField(max_length=100,null=True, blank=True)
    inactive = models.CharField(max_length=100,null=True, blank=True)
    working = models.CharField(max_length=100,null=True, blank=True)
    meeting = models.CharField(max_length=100,null=True, blank=True)
    on_break = models.CharField(max_length=100,null=True, blank=True)
    lunch_dinner = models.CharField(max_length=100,null=True, blank=True)
    auxiliary = models.CharField(max_length=100,null=True, blank=True)
    toilet = models.CharField(max_length=100,null=True, blank=True)


    history = HistoricalRecords()

    def __str__(self):
        return f"{self.name} - {self.team}"

class Rax_Utilization_FileUpload(models.Model):
    file = models.FileField(upload_to='rax_utilization', null=True, blank=True)
    upload_timestamp = models.DateTimeField(default=timezone.now)

    def insert_records_to_master_list(self):
        file_path = self.file.path
        sheet_name = "1 - RAX RAW"
        # Read the Excel file
        df = pd.read_excel(file_path, sheet_name=sheet_name)

        # Column mapping and renaming (your existing code)
        column_mapping = {
        'Quarter': 'quarter',
        'Region': 'region',
        'Team': 'team',
        'Manager': 'manager',
        'Month': 'month',
        'Date': 'date',
        'EID': 'eid',
        'Name': 'name',
        'Active %': 'active',
        'Idle %': 'idle',
        'Shrinkage %': 'shrinkage',
        'C_Active': 'c_active',
        'c_Idle': 'c_idle',
        'Overtime': 'overtime',
        'c_Shrinkages': 'c_shrinkages',
        'Inactive': 'inactive',
        'Working': 'working',
        'Meeting': 'meeting',
        'On Break': 'on_break',
        'Lunch/Dinner': 'lunch_dinner',
        'Auxiliary': 'auxiliary',
        'Toilet': 'toilet',
        }


        df.rename(columns=column_mapping, inplace=True)


        # Extract the required columns from the DataFrame
        columns = [
            'quarter', 'region', 'team', 'manager', 'month', 'date', 'eid', 'name', 'active', 'idle', 'shrinkage', 'c_active', 'c_idle', 'overtime', 'c_shrinkages', 'inactive',
            'working', 'meeting', 'on_break', 'lunch_dinner', 'auxiliary', 'toilet'
        ]
        data = df[columns]

        # Convert DataFrame to list of dictionaries
        records = data.to_dict('records')

        # Clean up string columns
        for record in records:
            for column in ['quarter', 'region', 'name', 'team', 'month', 'manager']:
                if isinstance(record[column], str):
                    record[column] = record[column].strip()

        
        existing_records = Rax_Utilization.objects.filter(
            Q(month__in=set(record['month'] for record in records)) &
            Q(region__in=set(record['region'] for record in records))
        )

        existing_records_dict = {(record.month, record.region): record for record in existing_records}

        new_records = [
            record for record in records
            if (record['month'], record['region']) not in existing_records_dict
        ]
                    

        # Initialize counter for the current sheet
        inserted_count = 0

        # Bulk insert the records for the current sheet
        with transaction.atomic():
            for record in new_records:
                # Check if both 'name' and 'month' are not blank
                if not pd.isna(record['name']) and not pd.isna(record['month']):
                    # Rax_Utilization.objects.create(**record)
                    Rax_Utilization.objects.create(**record)
                    inserted_count += 1

        # Return the total count of inserted records
        return inserted_count

    def save(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().save(*args, **kwargs)
        if request is not None:
            inserted_count = self.insert_records_to_master_list()
          
            if inserted_count > 0:
                message = f"{inserted_count} records were inserted."
                messages.success(request, message)


                

class Quality_Report(models.Model):
    region = models.CharField(max_length=25,null=True, blank=True)
    country = models.CharField(max_length=50,null=True, blank=True)
    data_source = models.CharField(max_length=10,null=True, blank=True)
    team = models.CharField(max_length=25,null=True, blank=True)
    data_stream = models.CharField(max_length=50,null=True, blank=True)
    frequency = models.CharField(max_length=5,null=True, blank=True)
    audit = models.CharField(max_length=50,null=True, blank=True)
    month = models.CharField(max_length=25,null=True, blank=True)
    checked = models.CharField(max_length=25,null=True, blank=True)
    errors = models.CharField(max_length=25,null=True, blank=True)
    accuracy = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)  # Change to DecimalField
    
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.country} - {self.team}"
    
class Quality_Report_FileUpload(models.Model):
    file = models.FileField(upload_to='quality_record', null=True, blank=True)
    upload_timestamp = models.DateTimeField(default=timezone.now)

    def insert_records_to_master_list(self):
        file_path = self.file.path
        sheet_name = "Raw data"
        # Read the Excel file
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        column_mapping = {
            'Region': 'region',
            'Country': 'country',
            'Data Source': 'data_source',
            'Team': 'team',
            'Data Stream': 'data_stream',
            'Frequency': 'frequency',
            'Audit': 'audit',
            'Month': 'month',
            'Checked': 'checked',
            'Errors': 'errors',
            'Accuracy': 'accuracy'
        }

        # Rename the columns in the DataFrame based on the mapping
        df.rename(columns=column_mapping, inplace=True)
        
        # Extract the required columns from the DataFrame
        columns = [
            'region','country', 'data_source', 'team', 'data_stream', 'frequency', 'audit',
            'month', 'checked', 'errors', 'accuracy'
        ]

        data = df[columns]
        # Convert NaN values in 'accuracy' column to 0
        data['accuracy'] = data['accuracy'].fillna(0)
        data['accuracy'] = data['accuracy'].apply(lambda x: None if pd.isna(x) else x)
        data['accuracy'] = data['accuracy'].apply(lambda x: float(x.rstrip('%')) / 100 if isinstance(x, str) else x)
        # Convert DataFrame to list of dictionaries
        records = data.to_dict('records')

        for record in records:
            for column in ['region', 'country', 'data_source', 'team', 'data_stream','frequency','audit','month','checked', 'errors', 'accuracy']:
                if isinstance(record[column], str):
                    record[column] = record[column].strip()
        
       # Initialize counters
        inserted_count = 0

        # Bulk insert the records
        with transaction.atomic():
            for record in records:
                
                # if isinstance(record['accuracy'], float):
                    # record['accuracy'] = f"{record['accuracy']:.2%}"
                
                Quality_Report.objects.create(**record)
                inserted_count += 1
                
        # Return the count of inserted
        return inserted_count

    def save(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().save(*args, **kwargs)
        if request is not None:
            inserted_count = self.insert_records_to_master_list()
          
            if inserted_count > 0:
                message = f"{inserted_count} records were inserted."
                messages.success(request, message)


        
                


    

    

    
  