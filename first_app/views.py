
from django.shortcuts import render
from first_app.models import  MasterList, Attrition, Attendance, Utilization, Quality, Service_Delivery, Productivity, Rax_Utilization, Quality_Report
from django.db.models import Count, Sum, DecimalField, Subquery, OuterRef
from decimal import Decimal
from django.http import JsonResponse
from django.db.models.functions import TruncMonth, Cast
from datetime import datetime, timedelta
from collections import defaultdict
from datetime import date, timedelta
from django.db.models import Count, Case, When, IntegerField, Func
import calendar
from calendar import month_abbr
from django.db.models import Count
from django.db.models import Min, Max
from django.db.models import Q
from calendar import monthrange
from collections import OrderedDict
from django.db.models import Avg
from django.http import HttpResponse, HttpResponseBadRequest
from django.db.models.functions import ExtractMonth
from django.http import QueryDict
from django.db.models import F, IntegerField, Case, When, Value
from django.db.models.functions import ExtractYear
from django.core.serializers import serialize
from django.db.models import Count, Case, When
import json
from django.db.models.functions import TruncDate
import html
from django.db.models import Value
from django.db.models import F, ExpressionWrapper, FloatField, fields
from dateutil.relativedelta import relativedelta
from itertools import groupby
import re
from django.utils import timezone
from django.db.models.functions import Lower, Round

# Create your views here.
def index(request):
    
    return render(request,'first_app/index.html')

def pages_contact(request):
    
    return render(request,'first_app/pages_contact.html')


def headcount(request, region):
    # current_year = datetime.now().year
    current_date, current_month, current_year = actual_first_day_of_the_month()
    region = region.upper()
    region_count = MasterList.objects.filter(region=region).count()
    previous_year_region_count = MasterList.objects.filter(region=region, hire_date__lt=date(current_year, 1, 1)).count()
    percentage_increase = 0
    if previous_year_region_count > 0:
        percentage_increase = ((region_count - previous_year_region_count) / previous_year_region_count) * 100

    new_employees_count = get_new_employees(region, current_year)
    previous_year = current_year - 1
    record_count_previous_year = MasterList.objects.filter(region=region, hire_date__year=previous_year).count()

    new_emp_percentage_increase = 0
    if record_count_previous_year > 0:
        new_emp_percentage_increase = ((new_employees_count - record_count_previous_year) / record_count_previous_year) * 100

    

    ma_count = manager_count(region)
    pieData = tenure(region)
    total_headcount = total_headcount_per_month(region)
    grade_counts = headcount_by_level(region)

    hired_employees = recently_hired_employees(region)

    employees = MasterList.objects.filter(region=region).order_by('hire_date')
    
    html= display_page_headcount(region)
    
    value = {"regions_headcount":region_count,"new_employees_count":new_employees_count,"manager_count":ma_count,
             "tenure_count":pieData,"headcounts_context":total_headcount,"grade_counts":grade_counts,
             "hired_employees":hired_employees,"employees":employees,"previous_year_region_count":previous_year_region_count,"percentage_increase":percentage_increase,
             "record_count_previous_year":record_count_previous_year,"new_emp_percentage_increase":new_emp_percentage_increase}    
    return render(request,html,context=value)

# def get_previous_employee_count(region, current_year, new_employees_count):
#     # Calculate the count for the previous year
#     start_date = date(current_year - 2, 1, 1)  # Year before the previous year
#     end_date = date(current_year - 1, 12, 31)   # Previous year
#     total_previous_year_count = MasterList.objects.filter(region=region, hire_date__range=(start_date, end_date)).count()
#     print(total_previous_year_count)
    
#     return total_previous_year_count

def display_page_headcount(region):
    html = ''
    if region == 'APAC':
        html = 'first_app/headcount_apac.html'
    if region == 'EMEA':
        html = 'first_app/headcount_emea.html'
    if region == 'USCA':
        html = 'first_app/headcount_usca.html'
    return html

def get_new_employees(region, current_year):
    record_count = MasterList.objects.filter(region=region,hire_date__year=current_year).count()
    return record_count

def manager_count(dept):
    m_count = MasterList.objects.filter(region=dept).values('tier_5', 'region').annotate(count=Count('id')).order_by('-region')
    return m_count

def recently_hired_employees(region):
    current_month = datetime.now().month - 1
    current_year = datetime.now().year
    recently_hired = MasterList.objects.filter(region=region,hire_date__month=current_month,hire_date__year=current_year).order_by('-hire_date')
    
    results = []
    for hired in recently_hired:
        emp_id = hired.emp_id
        first_name = hired.firstname
        last_name = hired.lastname
        job_titles = hired.job_title
        hired_date = hired.hire_date.strftime('%Y-%m-%d')
        department = hired.region
        results.append({'emp_id': emp_id, 'first_name': first_name, 'last_name': last_name, 'job_titles': job_titles,"hired_date": hired_date,'department':department})
    return results



# def calculate_headcount_by_region():
#     # Retrieve the minimum hire date to determine the year range
#     hire_date_range = MasterList.objects.aggregate(min_date=Min('hire_date'))
#     min_year = hire_date_range['min_date'].year
#     max_year = date.today().year # Use the current year as the maximum year


#     # Create a list of all years in the range
#     years = list(range(min_year, max_year + 1))
    
#     # Retrieve the employee count grouped by hire date year and department
#     data = (
#         MasterList.objects
#         .filter(hire_date__year__in=years)
#         .values('hire_date__year', 'region')
#         .annotate(count=Count('id'))
#         .order_by('hire_date__year', 'region')
#     )

    
#     departments = MasterList.objects.values_list('region', flat=True).distinct()
#     cumulative_counts = {}
#     previous_year_cumulative_counts = {}

#     filled_data = []

#     for department in departments:
#         # department_name = department.region
#         department_data = [item for item in data if item['region'] == department]

#         cumulative_counts.setdefault(department, 0)
#         previous_year_cumulative_counts.setdefault(department, 0)

#         for year in years:
#             item = next((item for item in department_data if item['hire_date__year'] == year), None)
#             if item:
#                 current_count = item['count']
#                 # print(year)

#                 # Calculate the resigned count for the current year and department
#                 resigned_count = (
#                     Attrition.objects
#                     .filter(
#                         Q(resignation_date__year=year) | Q(resignation_date__isnull=True),
#                         employee_id__hire_date__year__lte=year,
#                         employee_id__region=department,
#                         movement_type__movement_type="Attrition"
#                     )
#                     .values('employee_id')
#                     .distinct()
#                     .count()
#                 )
#                 # print(year)
#                 # print(resigned_count)
                
#                 current_count -= resigned_count
#                 cumulative_counts[department_name] += current_count
#                 item['cumulative_count'] = cumulative_counts[department_name]
                
                

#                 filled_item = {
#                     'hire_date__year': year,
#                     'department__department': department_name,
#                     'count': current_count,
#                     'cumulative_count': cumulative_counts[department_name],
#                     'percentage_increase': (
#                         round(
#                             ((cumulative_counts[department_name] - previous_year_cumulative_counts[department_name]) /
#                             previous_year_cumulative_counts[department_name]) * 100,
#                             2
#                         )
#                         if previous_year_cumulative_counts[department_name] != 0 else 0
#                     )
#                 }

#                 previous_year_cumulative_counts[department_name] = cumulative_counts[department_name]
#                 filled_data.append(filled_item)
#             else:
#                 filled_item = {
#                     'hire_date__year': year,
#                     'department__department': department_name,
#                     'count': 0,
#                     'cumulative_count': previous_year_cumulative_counts[department_name],
#                     'percentage_increase': 0
#                 }

#                 filled_data.append(filled_item)

#     last_items_per_department = {}
#     second_to_last_items_per_department = {}
#     for item in filled_data:
#         # print(item)
#         department = item['department__department']
#         second_to_last_items_per_department[department] = last_items_per_department.get(department)
#         last_items_per_department[department] = item

#     overall_headcount = last_items_per_department.get('APAC')['cumulative_count'] + last_items_per_department.get('EMEA')['cumulative_count'] + last_items_per_department.get('USCA')['cumulative_count']
#     previous_headcount = second_to_last_items_per_department.get('APAC')['cumulative_count'] + second_to_last_items_per_department.get('EMEA')['cumulative_count'] + second_to_last_items_per_department.get('USCA')['cumulative_count']
#     current_percentage = ((overall_headcount - previous_headcount) / previous_headcount) * 100
#     count = {
#         'last_item_apac': last_items_per_department.get('APAC'),
#         'last_item_emea': last_items_per_department.get('EMEA'),
#         'last_item_usca': last_items_per_department.get('USCA'),
#         'second_to_last_item_usca': second_to_last_items_per_department.get('USCA'),
#         'second_to_last_item_emea': second_to_last_items_per_department.get('EMEA'),
#         'second_to_last_item_apac': second_to_last_items_per_department.get('APAC'),
#         'overall_headcount':overall_headcount,
#         'previous_headcount':previous_headcount,
#         'current_percentage':current_percentage
#     }
#     return count


def headcount_by_level(dept):

    # Count the occurrences of each grade in the MasterList model
    grade_counts = MasterList.objects.values('grade').filter(region=dept).annotate(count=Count('grade'))
    # Extracting grade and count values
    grades = [item['grade'] for item in grade_counts]
    counts = [item['count'] for item in grade_counts]

    headcounts_job_level = []
    for grade, count in zip(grades, counts):
        headcounts_job_level.append({"name": str(grade), "value": count})

    return headcounts_job_level


def tenure(dept):

    today = date.today()
    more_than_15_years_start = today - timedelta(days=5475)
    tenure_count = ''
    if dept != '':
        tenure_count = MasterList.objects.filter(region=dept).annotate(
            tenure_group=Case(
                When(hire_date__gte=today - timedelta(days=365), then=1),
                When(hire_date__range=[today - timedelta(days=730), today - timedelta(days=365)], then=2),
                When(hire_date__range=[today - timedelta(days=1095), today - timedelta(days=730)], then=3),
                When(hire_date__range=[today - timedelta(days=1825), today - timedelta(days=1095)], then=4),
                When(hire_date__range=[today - timedelta(days=3650), today - timedelta(days=1825)], then=5),
                When(hire_date__range=[today - timedelta(days=5475), today - timedelta(days=3650)], then=6),
                When(hire_date__lt=more_than_15_years_start, then=7),
                default=None,
                output_field=IntegerField(),
            ),
        ).values('tenure_group').annotate(count=Count('id'))
    else:
        tenure_count = MasterList.objects.annotate(
            tenure_group=Case(
                When(hire_date__gte=today - timedelta(days=365), then=1),
                When(hire_date__range=[today - timedelta(days=730), today - timedelta(days=365)], then=2),
                When(hire_date__range=[today - timedelta(days=1095), today - timedelta(days=730)], then=3),
                When(hire_date__range=[today - timedelta(days=1825), today - timedelta(days=1095)], then=4),
                When(hire_date__range=[today - timedelta(days=3650), today - timedelta(days=1825)], then=5),
                When(hire_date__range=[today - timedelta(days=5475), today - timedelta(days=3650)], then=6),
                When(hire_date__lt=more_than_15_years_start, then=7),
                default=None,
                output_field=IntegerField(),
            ),
        ).values('tenure_group').annotate(count=Count('id'))
    
    pieData = []

    tenureGroupNames = {
    1: "<1yr",
    2: "1-2yr",
    3: "2-3yr",
    4: "3-5yr",
    5: "5-10yr",
    6: "10-15yr",
    7: "15+yr",
    }
    # Append each result to pieData
    for result in tenure_count:
        pieData.append({
            "value": result['count'],
            "name": tenureGroupNames[result['tenure_group']]
        })
    return pieData


def tenure_by_department(request):
    department = request.GET.get('department')
    today = date.today()
    more_than_15_years_start = today - timedelta(days=5475)

    tenure_count = MasterList.objects.filter(
        emp_status__status='Active',
        department__department=department
    ).annotate(
        tenure_group=Case(
            When(hire_date__gte=today - timedelta(days=365), then=1),
            When(hire_date__range=[today - timedelta(days=730), today - timedelta(days=365)], then=2),
            When(hire_date__range=[today - timedelta(days=1095), today - timedelta(days=730)], then=3),
            When(hire_date__range=[today - timedelta(days=1825), today - timedelta(days=1095)], then=4),
            When(hire_date__range=[today - timedelta(days=3650), today - timedelta(days=1825)], then=5),
            When(hire_date__range=[today - timedelta(days=5475), today - timedelta(days=3650)], then=6),
            When(hire_date__lt=more_than_15_years_start, then=7),
            default=None,
            output_field=IntegerField(),
        ),
    ).values('department', 'tenure_group').annotate(count=Count('id'))


    pieData = []

    tenureGroupNames = {
        1: "<1yr",
        2: "1-2yr",
        3: "2-3yr",
        4: "3-5yr",
        5: "5-10yr",
        6: "10-15yr",
        7: "15+yr",
    }

    # Append each result to pieData
    for result in tenure_count:
        pieData.append({
            # "department": result['department'],
            # "tenure_group": result['tenure_group'],
            "value": result['count'],
            "name": tenureGroupNames[result['tenure_group']]
        })

    return JsonResponse({"data": pieData})

def total_headcount_per_month(dept):

    # current_year = datetime.now().year
    # current_month = datetime.now().month
    current_date, current_month , current_year = actual_first_day_of_the_month()

    current_month_number = datetime.now().month
    months_range = range(1, current_month_number + 1)
    


    # Annotate the queryset to count headcounts by month for the current year
    headcount_by_month = MasterList.objects.filter(
        hire_date__year=current_year,region=dept
    ).annotate(
        month=TruncMonth('hire_date')
    ).values('month').annotate(count=Count('id')).order_by('month')

    # Calculate the total count of active employees before the current year
    total_count = (
        MasterList.objects.filter(hire_date__year__lt=current_year,region=dept)
        .aggregate(total_count=Count('id'))
    )['total_count']
    # Create a dictionary to store the headcounts for each month
    headcounts = {month_abbr: 0 for month_num, month_abbr in enumerate(calendar.month_abbr) if month_num != 0}
    

    # Update the headcounts dictionary with the annotated values, carrying forward previous month's headcount
    previous_count = total_count
    for month in months_range:
        month_abbr = calendar.month_abbr[month]

        # Check if there is headcount data for the current month
        count_data = headcount_by_month.filter(hire_date__month=month).first()
        # print(count_data)
        if count_data is not None:
            count = count_data['count']
            previous_count += count
        headcounts[month_abbr] = previous_count
    
    month_names = []
    counts = []

    for month_abbr in calendar.month_abbr[1:current_month_number + 1]:
        month_names.append(month_abbr)
        counts.append(headcounts[month_abbr])

    
    headcounts_context = {
        'months': month_names,
        'counts': counts,
        'current_year': current_year,
    }

    return headcounts_context


def tables(request):
    employees = MasterList.objects.all().order_by('hire_date')
    list_of_employees = {"employees":employees}
    return render(request,'first_app/tables-data.html',context=list_of_employees)

def login(request):
    return render(request,'first_app/login.html')





def attrition(request, region):
    region = region.upper()
    current_date , current_month, current_year = actual_first_day_of_the_month()
    
    number_of_resign = attrition_number_resign_month(region, current_year)
    reason_of_attrition = attrition_reason(region, current_year)
    attrition_based_tenure = attrition_by_tenure(region, current_year)
    attrition_per_manager_data = attrition_per_manager(region,current_year)

    value = {"number_of_resignees":number_of_resign,"reason_of_attrition":reason_of_attrition,
             "attrition_based_tenure":attrition_based_tenure,"attrition_per_manager_data":attrition_per_manager_data}
    html = display_page_attrition(region)
    
    
    return render(request, html, context=value)

def attrition_number_resign_month(region, current_year):
    # Filter by department and year
    resignations = Attrition.objects.filter(
        department=region,
        resignation_eff_date__year=current_year
    )

    # Aggregate data by month and count resignations
    month_counts = resignations.annotate(
        month=F('resignation_eff_date__month')
    ).values('month').annotate(resignees=Count('id')).order_by('month')

    # Process the data to convert month numbers to month names
    resignation_data = [
        {"month": calendar.month_abbr[entry['month']], "resignees": entry['resignees']}
        for entry in month_counts
    ]

    return resignation_data

def attrition_reason(region, current_year):
    # Filter by department and current year
    resignation_data = Attrition.objects.filter(
        resignation_eff_date__year=current_year,  # Filter by year
        department=region  # Filter by department
    ).values('reason').annotate(resignee_count=Count('id'))

    # Prepare the data for the pie chart
    pie_chart_data = [
        {'reason': item['reason'], 'count': item['resignee_count']}
        for item in resignation_data
    ]
    
    return pie_chart_data

def attrition_by_tenure(region, current_year):
    # Filter the data based on the current year and department
    attrition_data = Attrition.objects.filter(
        resignation_eff_date__year=current_year,  # Filter for the current year
        department=region  # Filter by department
    ).annotate(
        # Calculate tenure in days directly without casting
        tenure_days=ExpressionWrapper(
            F('resignation_eff_date') - F('date_hired'),  # Calculate difference between resignation and hire date
            output_field=fields.DurationField()
        )
    ).annotate(
        # Convert tenure_days (in days) to tenure_years by dividing by 365
        tenure_years=ExpressionWrapper(
            F('tenure_days') / timedelta(days=365),  # Convert tenure to years by dividing by 365 days
            output_field=fields.FloatField()
        )
    ).values('tenure_years').annotate(
        resignee_count=Count('id')  # Count the number of resignations per tenure
    ).order_by('tenure_years')  # Order the data by tenure years


    # Dictionary to hold the aggregated results
    result_dict = {}

    # Now, map the tenure_years into defined group names and aggregate the counts
    for record in attrition_data:
        tenure_years = record['tenure_years']
        
        # Group tenure into predefined categories
        if tenure_years < 1:
            tenure_group = "<1yr"
        elif 1 <= tenure_years < 2:
            tenure_group = "1-2yr"
        elif 2 <= tenure_years < 3:
            tenure_group = "2-3yr"
        elif 3 <= tenure_years < 5:
            tenure_group = "3-5yr"
        elif 5 <= tenure_years < 10:
            tenure_group = "5-10yr"
        elif 10 <= tenure_years < 15:
            tenure_group = "10-15yr"
        else:
            tenure_group = "15+yr"
        
        # If the tenure group already exists in the dictionary, add the resignee count
        if tenure_group in result_dict:
            result_dict[tenure_group] += record['resignee_count']  # Increment the count
        else:
            result_dict[tenure_group] = record['resignee_count']  # Initialize the count

    # Convert the aggregated data into a list of dictionaries
    result = [{'tenure_group': group, 'resignee_count': count} for group, count in result_dict.items()]

    return result

def attrition_per_manager(region, current_year):
    # Filter the data based on the current year and department
    attrition_data = Attrition.objects.filter(
        resignation_eff_date__year=current_year,  # Filter for the current year
        department=region  # Filter by department
    ).values('manager').annotate(
        resignee_count=Count('id')  # Count the number of resignations for each manager
    ).order_by('-resignee_count')  # Order by count descending

    # Convert data to a format suitable for the chart
    chart_data = [
        {'manager': record['manager'], 'count': record['resignee_count']}
        for record in attrition_data
    ]
    return chart_data
    


def display_page_attrition(region):
    html = ''
    if region == 'APAC':
        html = 'first_app/attrition_apac.html'
    if region == 'EMEA':
        html = 'first_app/attrition_emea.html'
    if region == 'USCA':
        html = 'first_app/attrition_usca.html'
    return html








def attrition_by_tenure_by_department(request):
    if request.method == 'GET':
        department = request.GET.get('department')
        current_year = datetime.now().year
        # print("attrition_by_tenure_by_department")
        # print(department)
        today = date.today()
        # more_than_15_years_start = today - timedelta(days=5475)

        tenure_count = Attrition.objects.filter(
            movement_type__movement_type='Attrition',
            resignation_date__year=current_year,
            resignation_date__lte=today,  # Filter for records on or before the current date
            employee_id__department__department=department
        ).annotate(
            tenure=ExtractYear(F('resignation_date')) - ExtractYear(F('employee_id__hire_date')),
            tenure_group=Case(
                When(tenure__lt=1, then=1),
                When(tenure__range=[1, 2], then=2),
                When(tenure__range=[2, 3], then=3),
                When(tenure__range=[3, 5], then=4),
                When(tenure__range=[5, 10], then=5),
                When(tenure__range=[10, 15], then=6),
                When(tenure__gte=15, then=7),
                default=None,
                output_field=IntegerField(),
            ),
        ).values('tenure_group').annotate(count=Count('id'))
        # print(tenure_count)

        pieData = []

        tenureGroupNames = {
            1: "<1yr",
            2: "1-2yr",
            3: "2-3yr",
            4: "3-5yr",
            5: "5-10yr",
            6: "10-15yr",
            7: "15+yr",
        }

        # Append each result to pieData
        for result in tenure_count:
            pieData.append({
                "value": result['count'],
                "name": tenureGroupNames[result['tenure_group']]
            })
    return JsonResponse({"data": pieData})



    

def percentage(region_count,overall_count):
    percent = (region_count / (overall_count+region_count)) * 100
    percent =round(percent, 2)
    return percent

# def process_data(data):
#     results = []
#     label = data.get('label')
#     months = data.get('month')
#     start_date = data.get('start')
#     end_date = data.get('end')

#     if (end_date == None or end_date ==""):
#             end_date = start_date
#     if (start_date != None and end_date != None):
#         start_date = datetime.strptime(start_date, '%m/%d/%Y').strftime('%Y-%m-%d')
#         end_date = datetime.strptime(end_date, '%m/%d/%Y').strftime('%Y-%m-%d')

#         data = Employees.objects.filter(status='Active', date__range=(start_date, end_date)).values('position','date').annotate(count=Count('position')).order_by('date','position')
#         chart_data = organize_data(data)
#         return chart_data
       
#     elif (months != None and months == 'yes'):

#         year = time.strftime("%Y")
#         month = time.strftime("%m")
#         data = Employees.objects.filter(status='Active',position=label,
#                                      date__month=month,
#                                      date__year=year).annotate(month=TruncMonth('date')).values('region').annotate(count=Count('region')).order_by('region')
#         for item in data: 
#             results.append({'region': item['region'],'count': item['count']})
#     else:
#         data = Employees.objects.filter(status='Active',position=label).values('region').annotate(count=Count('region')).order_by('region')
#         for item in data: 
#             results.append({'region': item['region'],'count': item['count']})

#     return results

# def position(request):
#     if request.method == 'GET':
#         data = request.GET.copy()
#         processed_data = process_data(data)
#     return JsonResponse(processed_data,safe=False)

def convert_date(end):
    date = datetime.strptime(end, '%m/%Y')
    last_day_of_month = (date.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    date = last_day_of_month.strftime('%Y-%m-%d') 

    return date

def organize_data(data):

    # Initialize dictionary to store data organized by date
    data_by_date = defaultdict(dict)

    # Iterate over queryset and add data to dictionary
    for row in data:
        date_str = row['date'].strftime('%B %Y')
        if row['position'] not in data_by_date[date_str]:
            data_by_date[date_str][row['position']] = row['count']
        else:
            data_by_date[date_str][row['position']] += row['count']

    # Create ChartJS data object
    chart_data = {
        'labels': [],
        'datasets': [],
    }

    # Create array to hold datasets for each position
    datasets = []

    # Get sorted set of positions
    positions = sorted(set([pos for date in data_by_date for pos in data_by_date[date]]))

    # Define colors for each position
    colors = ['#0b1d78', '#0045a5', '#0069c0', '#008ac5', '#00a9b5', '#00c698', '#1fe074']

    # Loop through the positions and create a dataset for each one
    for i, position in enumerate(positions):
        counts = []
        for date in data_by_date:
            if position in data_by_date[date]:
                counts.append(data_by_date[date][position])
            else:
                counts.append(0)
        datasets.append({
            'label': position,
            'data': counts,
            'backgroundColor': colors[i % len(colors)],
            'borderColor': colors[i % len(colors)],
            'borderWidth': 1
        })

    # Set the chart data with the datasets array
    chart_data['labels'] = list(data_by_date.keys())
    chart_data['datasets'] = datasets

    return chart_data



def fetch_firstname(request):
    
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        
        try:
            master_list = MasterList.objects.get(emp_id=employee_id)
            firstname = master_list.firstname
            lastname = master_list.lastname
            return JsonResponse({'firstname': firstname, 'lastname': lastname})
        except MasterList.DoesNotExist:
            pass
    return JsonResponse({'error': 'Invalid request'})

def dynamic_change_attrition(request):
    if request.method == 'POST':
        post_body = QueryDict(request.body)
        employee_id = post_body.get('employee_id')

        try:
            attrition_record = Attrition.objects.get(employee_id=employee_id)   
            response_data = {
                'movement_type': attrition_record.movement_type_id,
                'resignation_date': attrition_record.resignation_date,
                'reason': attrition_record.reason_id,
                'comment': attrition_record.comment,
                'success': 'yes'
            }
            return JsonResponse(response_data)
        except Attrition.DoesNotExist:
            return JsonResponse({'error': 'Attrition record does not exist'})
        

def attendance(request, region):
    # Get the current year
    region = region.upper()
    # current_year = datetime.now().year
    current_date , current_month, current_year = actual_first_day_of_the_month()    
    # scheduled_headcount = Attendance.objects.filter(region=region).exclude(type='PLANNED', att_date__year=current_year).count()
    scheduled_headcount = Attendance.objects.filter(
        Q(type='PRESENT') | Q(type='UNPLANNED'),region=region, att_date__year=current_year).count()
    

    attendance_rate = get_year_to_date_scheduled_hc(current_year,scheduled_headcount,region)
    planned_leave_rate = get_planned_rate(scheduled_headcount, current_year, region)
    unplanned_leave_rate = get_unplanned_rate(current_year,scheduled_headcount, region)
    percentage_monthly = get_monthly_attendance_rate(current_year, region)
    percentage_last_five_days = get_five_dates_percentage_rates(current_year, region)


    default_date_first_day, month = attendance_actual_first_day_of_the_month()
    default_date_last_day = attendance_actual_last_day_of_the_month()


    filtered_data = Attendance.objects.filter(att_date__range=[default_date_first_day, default_date_last_day], region=region)
    unique_prod_managers = filtered_data.exclude(prod_manager=None).exclude(prod_manager='nan').values_list('prod_manager', flat=True).distinct()
    unique_assoc_managers = filtered_data.exclude(assoc_manager=None).exclude(assoc_manager='nan').values_list('assoc_manager', flat=True).distinct()
    unique_tleads = filtered_data.exclude(tlead=None).exclude(tlead='nan').values_list('tlead', flat=True).distinct()
    team = filtered_data.exclude(team__in=[None,'NaN', 'nan']).values_list('team',flat=True).distinct()

    team_counts = filtered_data.values('team').annotate(
    present_count=Count('type', filter=Q(type='PRESENT')),
    planned_count=Count('type', filter=Q(type='PLANNED')),
    restday_count=Count('type', filter=Q(type='RESTDAY')),
    unplanned_count=Count('type', filter=Q(type='UNPLANNED'))
    )

    total_filtered_date_data = get_filtered_date_data(filtered_data)

    daily_attendance = get_daily_attendance(region)

    html = display_page(region)

    
    att = {"attendance_rate":attendance_rate,"planned_leave_rate":planned_leave_rate,"unplanned_leave_rate":unplanned_leave_rate,
           "percentage_monthly":percentage_monthly,"percentage_last_five_days":percentage_last_five_days,
          "default_date_first_day":default_date_first_day,
           "default_date_last_day":default_date_last_day,"unique_prod_managers":unique_prod_managers, 
           "unique_assoc_managers":unique_assoc_managers,"unique_tleads":unique_tleads,"team":team,"team_counts":team_counts,"total_filtered_date_data":total_filtered_date_data,"daily_attendance":daily_attendance}
    return render(request,html,context=att)

def display_page(region):
    html = ''
    if region == 'APAC':
        html = 'first_app/attendance_apac.html'
    if region == 'EMEA':
        html = 'first_app/attendance_emea.html'
    if region == 'USCA':
        html = 'first_app/attendance_usca.html'
    return html



def get_daily_attendance(region):

    current_date = datetime.now()
    # current_date = datetime(2023, 9, 1)
    # Calculate the date of the previous weekday (excluding Saturday and Sunday)
    one_day = timedelta(days=1)
    previous_weekday = current_date - one_day
    formatted_current_date = previous_weekday.strftime("%b-%d")

    
    while previous_weekday.weekday() >= 5:  # 5 represents Saturday, 6 represents Sunday
        previous_weekday -= one_day
    # Query the Attendance table for data on the previous weekday
    previous_weekday_count = Attendance.objects.filter(att_date=previous_weekday,region=region).exclude(type="RESIGNED").count()
    previous_schedule_hc = Attendance.objects.filter(Q(type='PRESENT') | Q(type='UNPLANNED'), att_date=previous_weekday,region=region).count()
    previous_present = Attendance.objects.filter(type='PRESENT', att_date=previous_weekday,region=region).count()
    previous_planned = Attendance.objects.filter(type='PLANNED', att_date=previous_weekday,region=region).count()
    previous_restday = Attendance.objects.filter(type='RESTDAY', att_date=previous_weekday,region=region).count()
    previous_unplanned = Attendance.objects.filter(type='UNPLANNED', att_date=previous_weekday,region=region).count()
   
    att = {"previous_weekday_count":previous_weekday_count,"previous_schedule_hc":previous_schedule_hc,"previous_present":previous_present,"previous_planned":previous_planned,"previous_unplanned":previous_unplanned,"previous_restday":previous_restday,
           "formatted_current_date":formatted_current_date}
    return att



def get_filtered_date_data(filtered_data):
    planned_count = filtered_data.filter(type='PLANNED').count()
    unplanned_count = filtered_data.filter(type='UNPLANNED').count()
    present_count = filtered_data.filter(type='PRESENT').count()
    restday_count = filtered_data.filter(type='RESTDAY').count()
    scheduled_headcount = filtered_data.filter(type__in=['PRESENT', 'UNPLANNED']).count()
    headcount = filtered_data.exclude(type='RESIGNED').count()

    planned_rate = planned_count / headcount * 100 if headcount != 0 else 0
    unplanned_rate = unplanned_count / headcount * 100 if headcount != 0 else 0
    # Calculate the attendance rate
    attendance_rate = present_count / scheduled_headcount * 100 if scheduled_headcount != 0 else 0
    # Prepare the data to be sent in the JSON response
    computed_data = {
        'planned_count': planned_count,
        'unplanned_count': unplanned_count,
        'restday_count':restday_count,
        'present_count': present_count,
        'scheduled_headcount': scheduled_headcount,
        'headcount': headcount,
        'planned_rate': planned_rate,
        'unplanned_rate': unplanned_rate,
        'attendance_rate': attendance_rate,
    }
    return computed_data


def get_year_to_date_scheduled_hc(current_year, scheduled_headcount, region):
    # print(current_year)
    # COUNT ALL WITH PRESENT TYPE
    present_count = Attendance.objects.filter(type='PRESENT', att_date__year=current_year, region=region).count()
    if scheduled_headcount > 0:
        attendance_rate = present_count / scheduled_headcount
    else:
        attendance_rate = 0.0 
    
    return attendance_rate

def get_planned_rate(scheduled_headcount, current_year, region):
    planned_count = Attendance.objects.filter(type='PLANNED', att_date__year=current_year, region=region).count()
    rest_day_count = Attendance.objects.filter(type='RESTDAY', att_date__year=current_year, region=region).count()
    headcount = scheduled_headcount + planned_count + rest_day_count
    

    if headcount > 0:
        planned_leave_rate = planned_count / headcount
    else:
        planned_leave_rate = 0.0  # Handle the case when there are no total counts

    return planned_leave_rate

def get_unplanned_rate(current_year,scheduled_headcount, region):
    unplanned_count = Attendance.objects.filter(type='UNPLANNED', att_date__year=current_year, region=region).count()
    unplanned_leave_rate = 0

    if scheduled_headcount > 0:
        unplanned_leave_rate = unplanned_count / scheduled_headcount
    
    return unplanned_leave_rate

def get_monthly_attendance_rate(current_year,region):
    # GET SCHEDULED HC BY EXCLUDING PLANNED IN THE COUNT
    # Query to get the count per month
    

    scheduled_headcount_monthly_counts = Attendance.objects.filter(
        Q(type='PRESENT') | Q(type='UNPLANNED'),region=region, att_date__year=current_year).values('att_date__month','region').annotate(count=Count('id'))

    present_count_monthly = Attendance.objects.filter(type='PRESENT', att_date__year=current_year, region=region).values('att_date__month','region') \
        .annotate(count=Count('id'))
    percentage_monthly = []

    for scheduled_count in scheduled_headcount_monthly_counts:
        month = scheduled_count['att_date__month']
        region = scheduled_count['region']
        scheduled_count_value = scheduled_count['count']
        
        present_counts = present_count_monthly.filter(att_date__month=month)
        if present_counts.exists():
            present_count_value = present_counts[0]['count']
            percentage = present_count_value / scheduled_count_value
            percentage_monthly.append({'month': month, 'percentage': percentage,'region': region})

    return percentage_monthly


def get_five_dates_percentage_rates(current_year, region):
    # Filter the Attendance_APAC model for the latest 5 days
    latest_five_days_scheduled = Attendance.objects.filter(Q(type='PRESENT') | Q(type='UNPLANNED'),region=region, att_date__year=current_year) \
    .order_by('-att_date') \
    .values('att_date') \
    .annotate(count=Count('id')) \
    .values('att_date', 'count')[:5]


    latest_five_days_present = Attendance.objects.filter(type='PRESENT', att_date__year=current_year,region=region) \
    .order_by('-att_date') \
    .values('att_date') \
    .annotate(count=Count('id')) \
    .values('att_date', 'count')[:5]

    percentage_last_five_days = []

    for scheduled_count_days in latest_five_days_scheduled:
        att_date = scheduled_count_days['att_date']
        scheduled_count__days_value = scheduled_count_days['count']
        
        present_count_entry = next(
            (entry for entry in latest_five_days_present if entry['att_date'] == att_date), 
            None
        )
        
        if present_count_entry:
            present_count_days_value = present_count_entry['count']
            percentage_days = present_count_days_value / scheduled_count__days_value
            percentage_last_five_days.append({'att_date': att_date, 'percentage': percentage_days})
    

    percentage_last_five_days = [
    {
        'att_date': entry['att_date'].strftime('%Y-%m-%d'),
        'percentage': entry['percentage']
    }
    for entry in percentage_last_five_days]

    return percentage_last_five_days


def first_day_of_the_month():
    # Get the current year and month
    today = datetime.today()
    year = today.year
    month = today.month - 3

    # Calculate the first day of the current month
    first_day_of_month = datetime(year, month, 1)
    # print(first_day_of_month, month)
    return str(first_day_of_month.date()), month

def last_day_of_the_month():
    # Get the current year and month
    today = datetime.today()
    year = today.year
    month = today.month - 3

    # Calculate the last day of the current month
    # Get the first day of the next month
    first_day_of_next_month = datetime(year, month % 12 + 1, 1)

    # Calculate the last day of the current month by subtracting one day from the first day of the next month
    last_day_of_month = first_day_of_next_month - timedelta(days=1)
    return str(last_day_of_month.date())

# def actual_first_day_of_the_month():
#     # Get the current year and month
#     today = datetime.today()
#     year = today.year
#     month = today.month - 3

#     # Calculate the first day of the current month
#     first_day_of_month = datetime(year, month, 1)
#     return str(first_day_of_month.date()), month

# def attendance_actual_first_day_of_the_month():
#     # Get the current year and month
#     today = datetime.today()
#     year = today.year
#     month = today.month - 1

#     # Calculate the first day of the current month
#     first_day_of_month = datetime(year, month, 1)
#     return str(first_day_of_month.date()), month

def with_last_year_data_first_day_of_the_month():
    # Get the current date
    today = datetime.now()
    # today = datetime(2024, 4, 1)

    # Calculate the first day of the current month
    first_day_of_month = today.replace(day=1)

    # Calculate the first day of the previous month
    first_day_of_previous_month = first_day_of_month - timedelta(days=1)

    # Get the year and month of the previous month
    year = first_day_of_previous_month.year
    month = first_day_of_previous_month.month

    # Adjust month and year if current month is January
    if today.month <= 12:
        month = 12  
        year -= 1   # Decrement year

    first_day = f"{year}-{month:02d}-01"
    # print(first_day)
    return first_day, month, year

def actual_first_day_of_the_month():
    # Get the current date
    today = datetime.now()

    # Calculate the first day of the current month
    first_day_of_month = today.replace(day=1)

    # Calculate the first day of the previous month
    first_day_of_previous_month = first_day_of_month - timedelta(days=1)

    # Get the year and month of the previous month
    year = first_day_of_previous_month.year
    month = first_day_of_previous_month.month

    # if month == 1:
    #     # No data for January, set month and year to December of the previous year
    #     month = 12
    #     year -= 1

    first_day = f"{year}-{month:02d}-01"
    # print(first_day)
    return first_day, month , year

def last_year_actual_last_day_of_the_month():
    # Set the year and month
    year = 2023
    month = 12  # December

    # Calculate the last day of the month
    last_day_of_month = datetime(year, month, 1) + timedelta(days=31)
    while last_day_of_month.month != month:
        last_day_of_month -= timedelta(days=1)
    return str(last_day_of_month.date())

def attendance_actual_first_day_of_the_month():
    # Get the current date
    today = datetime.now()

    # Calculate the first day of the current month
    first_day_of_month = today.replace(day=1)

    # Calculate the first day of the previous month
    first_day_of_previous_month = first_day_of_month - timedelta(days=1)

    # Get the year and month of the previous month
    year = first_day_of_previous_month.year
    month = first_day_of_previous_month.month

    first_day = f"{year}-{month:02d}-01"

    return first_day, month 

def attendance_actual_last_day_of_the_month():
    # Get the current year and month
    today = datetime.today()
    year = today.year
    month = today.month - 1

    # Calculate the last day of the current month
    # Get the first day of the next month
    first_day_of_next_month = datetime(year, month % 12 + 1, 1)

    # Calculate the last day of the current month by subtracting one day from the first day of the next month
    last_day_of_month = first_day_of_next_month - timedelta(days=1)
    return str(last_day_of_month.date())

# def actual_last_day_of_the_month():
#     # Get the current year and month
#     today = datetime.today()
#     year = today.year
#     month = today.month - 2

#     # Calculate the last day of the current month
#     # Get the first day of the next month
#     first_day_of_next_month = datetime(year, month % 12 + 1, 1)

#     # Calculate the last day of the current month by subtracting one day from the first day of the next month
#     last_day_of_month = first_day_of_next_month - timedelta(days=1)
#     return str(last_day_of_month.date())

def actual_last_day_of_the_month():
    # Get the current date
    today = datetime.now()

    # Calculate the first day of the current month
    first_day_of_month = today.replace(day=1)

    # Calculate the first day of the previous month
    first_day_of_previous_month = first_day_of_month - timedelta(days=1)

    # Get the year and month of the previous month
    year = first_day_of_previous_month.year
    month = first_day_of_previous_month.month

    # Calculate the last day of the previous month using the monthrange function
    last_day = monthrange(year, month)[1]

    return f"{year}-{month:02d}-{last_day:02d}"  



def get_assoc_managers(request):
    selected_prod_managers = request.GET.getlist('selected_prod_managers[]', [])
    # Filter Associate Managers based on selected Prod. Managers
    assoc_managers_data = Attendance.objects.filter(prod_manager__in=selected_prod_managers).exclude(assoc_manager='nan').values('assoc_manager', 'tlead', 'team').distinct()

    # Convert the QuerySet to a list
    assoc_managers_list = list(assoc_managers_data)

    return JsonResponse({"assoc_managers": assoc_managers_list})

def get_team_leads(request):
    selected_assoc_managers = request.GET.getlist('selected_assoc_managers[]', [])
    team_leads = Attendance.objects.filter(
        assoc_manager__in=selected_assoc_managers
    ).exclude(tlead='nan').values_list('tlead', 'team').distinct()

    return JsonResponse({'team_leads': list(team_leads)})


def get_teams(request):
    selected_team_leads = request.GET.getlist('selected_team_leads[]', [])
    teams = Attendance.objects.filter(
        tlead__in=selected_team_leads
    ).exclude(team='nan').values_list( 'team').distinct()

    return JsonResponse({'teams': list(teams)})

def get_computations(request):
    selected_prod_managers = request.GET.getlist('selected_prod_managers[]', [])
    selected_assoc_managers = request.GET.getlist('selected_assoc_managers[]', [])
    selectedTeamLead = request.GET.getlist('selectedTeamLead[]', [])
    selectedTeam = request.GET.getlist('selectedTeam[]', [])
    from_date = request.GET.get('from_date', None)
    to_date = request.GET.get('to_date', None)
    region = request.GET.get('region')
    region = region.upper()

    filtered_data = Attendance.objects.none()
    

    if from_date and to_date:
        filtered_data = Attendance.objects.filter(att_date__range=[from_date, to_date],region=region)
        unique_prod_managers = filtered_data.exclude(prod_manager=None).exclude(prod_manager='nan').values_list('prod_manager', flat=True).distinct()
        unique_assoc_managers = filtered_data.exclude(assoc_manager=None).exclude(assoc_manager='nan').values_list('assoc_manager', flat=True).distinct()
        unique_tleads = filtered_data.exclude(tlead=None).exclude(tlead='nan').values_list('tlead', flat=True).distinct()
        team = filtered_data.exclude(team__in=[None,'NaN', 'nan']).values_list('team',flat=True).distinct()
        
    if selected_prod_managers:
        filtered_data = filtered_data.filter(prod_manager__in=selected_prod_managers)

    if selected_assoc_managers:
        filtered_data = filtered_data.filter(assoc_manager__in=selected_assoc_managers)

    if selectedTeamLead:
        filtered_data = filtered_data.filter(tlead__in=selectedTeamLead)

    if selectedTeam:
        filtered_data = filtered_data.filter(team__in=selectedTeam)

    grouped_data = get_computation_filter_button_click_table(filtered_data)
    computed_data_filter = get_computation_filter_button_click(filtered_data)
    total_computation_by_filter = get_computation_filter_button_click_total(filtered_data)

    return JsonResponse({'grouped_data': list(grouped_data),'computed_data_filter': computed_data_filter,"total_computation_by_filter":total_computation_by_filter,
                         'unique_prod_managers':list(unique_prod_managers),'unique_assoc_managers':list(unique_assoc_managers),'unique_tleads':list(unique_tleads),'team':list(team) }, safe=False)


def get_computation_filter_button_click(filtered_data):
    if filtered_data:
        planned_count = filtered_data.filter(type='PLANNED').count()
        unplanned_count = filtered_data.filter(type='UNPLANNED').count()
        restday_count = filtered_data.filter(type='RESTDAY').count()
        present_count = filtered_data.filter(type='PRESENT').count()
        scheduled_headcount = filtered_data.filter(type__in=['PRESENT', 'UNPLANNED']).count()
        headcount = scheduled_headcount + planned_count + restday_count

        planned_rate = 0
        unplanned_rate = 0
        attendance_rate = 0
        # Calculate the planned rate and unplanned rate
        if headcount != 0:
            planned_rate = planned_count / headcount * 100
        if scheduled_headcount !=0:
            unplanned_rate = unplanned_count / scheduled_headcount * 100
            attendance_rate = present_count / scheduled_headcount * 100

        

        # Prepare the data to be sent in the JSON response
        computed_data_filter = {
            'planned_count': planned_count,
            'unplanned_count': unplanned_count,
            'restday_count':restday_count,
            'present_count': present_count,
            'scheduled_headcount': scheduled_headcount,
            'headcount': headcount,
            'planned_rate': planned_rate,
            'unplanned_rate': unplanned_rate,
            'attendance_rate': attendance_rate,
        }

        return computed_data_filter

def get_computation_filter_button_click_table(filtered_data):
    # Group the data by team and annotate the scheduled headcount, planned count, and unplanned count
    grouped_data = filtered_data.values('team').annotate(
        present_count=Sum(Case(When(type='PRESENT', then=1), default=0, output_field=IntegerField())),
        planned_count=Sum(Case(When(type='PLANNED', then=1), default=0, output_field=IntegerField())),
        unplanned_count=Sum(Case(When(type='UNPLANNED', then=1), default=0, output_field=IntegerField())),
        restday_count=Sum(Case(When(type='RESTDAY', then=1), default=0, output_field=IntegerField()))
    )

     # Compute the planned and unplanned rates for each group
    for entry in grouped_data:
        scheduled_headcount = entry['present_count'] + entry['unplanned_count']
        headcount = scheduled_headcount + entry['planned_count'] + entry['restday_count']
        entry['headcount'] = headcount
        entry['scheduled_headcount'] = scheduled_headcount
        entry['planned_rate'] = (entry['planned_count'] / headcount) * 100 if headcount > 0 else 0
        entry['unplanned_rate'] = (entry['unplanned_count'] / scheduled_headcount) * 100 if scheduled_headcount > 0 else 0
        entry['attendance_rate'] = (entry['present_count'] / scheduled_headcount) * 100 if scheduled_headcount > 0 else 0

    return grouped_data


def get_computation_filter_button_click_total(filtered_data):

    # Calculate the overall statistics without grouping by team
    present_count = filtered_data.filter(type='PRESENT').count()
    planned_count = filtered_data.filter(type='PLANNED').count()
    restday_count = filtered_data.filter(type='RESTDAY').count()
    unplanned_count = filtered_data.filter(type='UNPLANNED').count()
    scheduled_headcount = filtered_data.filter(type__in=['PRESENT', 'UNPLANNED']).count()
    headcount = scheduled_headcount + planned_count + restday_count


    # total_count = present_count + unplanned_count
    # headcount = total_count + planned_count

    planned_rate = 0
    unplanned_rate = 0
    attendance_rate = 0
    # Calculate the planned rate and unplanned rate
    if headcount != 0:
        planned_rate = planned_count / headcount * 100
    if scheduled_headcount !=0:
        unplanned_rate = unplanned_count / scheduled_headcount * 100
        attendance_rate = present_count / scheduled_headcount * 100


    # Create a dictionary to hold the computed data
    computed_data = {
        'present_count': present_count,
        'planned_count': planned_count,
        'unplanned_count': unplanned_count,
        'restday_count':restday_count,
        'scheduled_headcount': scheduled_headcount,
        'headcount': headcount,
        'planned_rate': planned_rate,
        'unplanned_rate': unplanned_rate,
        'attendance_rate': attendance_rate,
    }

    return computed_data

def utilization(request, region):
    region = region.upper()

    # Get the current year
    # current_year = datetime.now().year

    # first_date, current_month, current_year = actual_first_day_of_the_month()
    first_date, current_month, current_year = with_last_year_data_first_day_of_the_month()
    print(current_year)
    last_date = last_year_actual_last_day_of_the_month()

    available_team = Utilization.objects.filter(region=region).values_list('team', flat=True).distinct().order_by('team')
    # available_team = [team.strip() for team in team_values]
    
    first_team = available_team.first()
    first_team_unescape = html.unescape(first_team)
    
    data_for_team = Utilization.objects.filter(
        shift_start__year=current_year,
        shift_start__month=current_month,
        team=first_team,
        region=region
    )

    # Group the data by employee and week
    employee_week_data = data_for_team.values('name', 'team','week').annotate(total_hours=Sum('duration_hour'))

    # Create a dictionary to hold the grouped data
    grouped_data = {}
    

    # Aggregate the total hours for each week for each employee
    for employee_week in employee_week_data:
        name = employee_week['name']
        team = employee_week['team']
        week = int(employee_week['week'].split()[1])  # Extract the numeric week value
        total_hours = float(employee_week['total_hours'])
        
        if name not in grouped_data:
            grouped_data[name] = {
                'team': team,
                f'week_{week}': total_hours,
                'total_hours_all_weeks': total_hours,
            }
        else:
            grouped_data[name][f'week_{week}'] = total_hours
            grouped_data[name]['total_hours_all_weeks'] += total_hours

    total_week_1 = 0
    total_week_2 = 0
    total_week_3 = 0
    total_week_4 = 0
    total_hours_new = 0
    total_util_percent = 0
    target_hours_per_month = 150
    for name, hours_by_week in grouped_data.items():
        total_hours_all_weeks = hours_by_week['total_hours_all_weeks']
        utilization_percentage = (total_hours_all_weeks / target_hours_per_month) * 100
        utilization_percentage = utilization_percentage  # Round to 2 decimal places

        hours_by_week['utilization_percentage'] = utilization_percentage

        total_week_1 += hours_by_week.get('week_1', 0)
        total_week_2 += hours_by_week.get('week_2', 0)
        total_week_3 += hours_by_week.get('week_3', 0)
        total_week_4 += hours_by_week.get('week_4', 0)
        total_hours_new += hours_by_week['total_hours_all_weeks']
        total_util_percent += hours_by_week['utilization_percentage']
    
    # Calculate the average utilization percentage
    num_employees = len(grouped_data)
    average_utilization_percentage = total_util_percent / num_employees if num_employees != 0 else 0

    grand_total = {
        'total_week_1': total_week_1,
        'total_week_2': total_week_2,
        'total_week_3': total_week_3,
        'total_week_4': total_week_4,
        'total_hours': total_hours_new,
        'average_utilization_percentage': average_utilization_percentage,
    }

    grouped_category, week_sums_category = grouped_by_category(first_team,region,current_month,current_year)
    all_keys = grouped_category.keys()
    all_keys_list = list(all_keys)

    utilization_data_monthly, highest_util, lowest_util = get_monthly_utlization_rate(current_year, region)

    weekly_sum_data, drilldown_data = weekly_util(grouped_category)

    top_five_util = get_top_5_names_with_highest_duration(region)
    overall_util_prercentage = overall_utilization(region)
    highest_hours_by_subtask = get_top_subtask_duration(region)
    break_adherence = get_break_adherence(region,current_year)
    util_per_country = utilization_per_country(region,current_year)
    overall_highest_utilization = overall_highest_utilization_country(region,current_year)
    html_page = display_page_utilization(region)

    value = {"grouped_data":grouped_data,"available_team":available_team,"first_team":first_team_unescape,
             "first_date":first_date,"last_date":last_date,"grouped_category":grouped_category,"all_keys":all_keys_list,
             "utilization_data_monthly":utilization_data_monthly,"highest_util":highest_util,"lowest_util":lowest_util,"grand_total":grand_total,"week_sums_category":week_sums_category, "weekly_sum_data":weekly_sum_data,
             "drilldown_data":drilldown_data,"top_five_util":top_five_util,"highest_hours_by_subtask":highest_hours_by_subtask,"overall_util_prercentage":overall_util_prercentage,
             "break_adherence":break_adherence,"util_per_country":util_per_country,"overall_highest_utilization":overall_highest_utilization}
    return render(request,html_page, context=value)

def utilization_per_country(region, current_year):

    # Filter records for the current year
    records = Utilization.objects.filter(shift_start__year=current_year, region=region)

    # Annotate the total duration_hour for each country and month
    annotated_records = records.values('country', 'shift_start__month').annotate(
        total_duration_hour=Sum('duration_hour'),
        total_employees=Count('name', distinct=True)
    )

    utilization_data = []
    for record in annotated_records:
        total_duration_hour = record['total_duration_hour'] or 0
        total_employees = record['total_employees'] or 0
        target_hours_per_employee = 150

        utilization_percentage = (total_duration_hour / (target_hours_per_employee * total_employees)) * 100

        utilization_data.append({
            'country': record['country'],
            'month': record['shift_start__month'],
            'utilization_percentage': round(utilization_percentage, 2)
        })
    

    
    return utilization_data

def overall_highest_utilization_country(region, current_year):
    # Filter records for the current year
    records = Utilization.objects.filter(shift_start__year=current_year, region=region)

    # Annotate the total duration_hour for each country and month
    annotated_records = records.values('country', 'shift_start__month').annotate(
        total_duration_hour=Sum('duration_hour'),
        total_employees=Count('name', distinct=True),
    )

    # Calculate monthly utilization percentage and accumulate for each country
    utilization_data = {}
    for record in annotated_records:
        total_duration_hour = record['total_duration_hour'] or 0
        total_employees = record['total_employees'] or 1  # to avoid division by zero

        target_hours_per_employee = 150

        monthly_utilization_percentage = (total_duration_hour / (target_hours_per_employee * total_employees)) * 100

        # Accumulate monthly percentages for each country
        country = record['country']
        if country not in utilization_data:
            utilization_data[country] = {
                'total_percentage': 0,
                'num_months': 0,
            }

        utilization_data[country]['total_percentage'] += monthly_utilization_percentage
        utilization_data[country]['num_months'] += 1

    # Calculate overall utilization percentage for each country
    overall_utilization_data = []
    for country, data in utilization_data.items():
        average_percentage = data['total_percentage'] / data['num_months']
        overall_utilization_data.append({
            'country': country,
            'overall_utilization_percentage': round(average_percentage, 2)
        })

    # Find the country with the highest overall utilization
    highest_utilization_country = max(overall_utilization_data, key=lambda x: x['overall_utilization_percentage'])
    # print(utilization_data)
    # print(highest_utilization_country)

    return highest_utilization_country


def overall_utilization(region):
    # Define the required hours per month
    required_hours_per_month = 150.0

    # current_year = datetime.now().year
    # current_date, current_month, current_year = actual_first_day_of_the_month()
    current_date, current_month, current_year = with_last_year_data_first_day_of_the_month()
    employee_data = (
        Utilization.objects.exclude(subtask__in=['Break 1', 'Break 2','Non-production Meetings','Non Production Meeting','Non-Production Meetings'])
        .filter(shift_start__year=current_year, region=region)
        .values('name', 'shift_start__month')
        .annotate(total_worked_hours=Sum(F('duration_hour')))
    )

    # Calculate individual utilization for each employee and store in a list
    individual_utils = {}
    for data in employee_data:
        employee_name = data['name']
        total_worked_hours = data['total_worked_hours']
        month = data['shift_start__month']

        if employee_name not in individual_utils:
            individual_utils[employee_name] = {
                'total_worked_hours': 0.0,
                'required_hours': 0.0,
            }

        individual_utils[employee_name]['total_worked_hours'] += total_worked_hours
        individual_utils[employee_name]['required_hours'] += required_hours_per_month
    # Calculate individual and average utilization
    average_utilization = 0.0
    for employee_name, data in individual_utils.items():
        total_worked_hours = data['total_worked_hours']
        required_hours = data['required_hours']

        individual_utilization = (total_worked_hours / required_hours) * 100
        # print(f"{employee_name}: {individual_utilization:.2f}%")
        average_utilization += individual_utilization

    average_utilization /= len(individual_utils)

    # print(f"Average Utilization for {current_year}: {average_utilization:.2f}%")
    return average_utilization

def get_break_adherence(region, current_year):

    # first_day_of_current_month, month = first_day_of_the_month()
    # current_date, current_month, current_year = actual_first_day_of_the_month()
    current_date, current_month, current_year = with_last_year_data_first_day_of_the_month()

    # Filter data for the current month
    utilization_data = Utilization.objects.filter(region=region,
        subtask__in=["Break 1", "Break 2"], 
        shift_start__month=current_month,
        shift_start__year=current_year
    )

    # Group data by team and calculate the total break time taken by each team
    employee_break_data = utilization_data.values("team", "name").annotate(
    total_break_time=Sum("time_spent_in_min"),
    days_with_break=Count("shift_start__date", distinct=True))
    
    team_data = {}
    team_break_data = {}
    for employee_data in employee_break_data:
        team_name = employee_data["team"]
        total_break_time = employee_data["total_break_time"] or 0
        total_days_with_breaks = employee_data["days_with_break"]
        
        if team_name in team_data:
            team_data[team_name]["total_break_time"] += total_break_time
            team_data[team_name]["total_days_with_breaks"] += total_days_with_breaks
        else:
            team_data[team_name] = {
                "total_break_time": total_break_time,
                "total_days_with_breaks": total_days_with_breaks
            }
    formatted_team_data = []
    for team_name, data in team_data.items():
        total_break_time = data["total_break_time"]
        total_days_with_breaks = data["total_days_with_breaks"]
        total_allowed_break_time = 30 * total_days_with_breaks  # Total allowed break time for the team
        break_adherence_percentage = (total_break_time / total_allowed_break_time) * 100


        formatted_data = {
        'team_name': team_name,
        'total_days_with_breaks': total_days_with_breaks,
        'break_adherence_percentage':break_adherence_percentage
        }
        formatted_team_data.append(formatted_data)
    # Sort the data based on break_adherence_percentage in descending order
    formatted_team_data = sorted(formatted_team_data, key=lambda x: x['break_adherence_percentage'], reverse=False)


    return formatted_team_data

def get_break_adherence_drilldown(request):
    selected_team = request.GET.get('team')
    # print(selected_team)
    region = request.GET.get('region')
    region = region.upper()
    # current_year = datetime.now().year

    first_day_of_current_month, month, current_year = with_last_year_data_first_day_of_the_month()

    # Filter data for the current month
    utilization_data = Utilization.objects.filter(region=region,team=selected_team,
        subtask__in=["Break 1", "Break 2"], 
        shift_start__month=month,
        shift_start__year=current_year
    )

    # Group data by team and calculate the total break time taken by each team
    employee_break_data = utilization_data.values("name").annotate(
    total_break_time=Sum("time_spent_in_min"),
    days_with_break=Count("shift_start__date", distinct=True))

    break_adherence_drilldown = []
    # Calculate and print the percentage of break adherence for each team
    for employee_data in employee_break_data:
        # team_name = employee_data["team"]
        employee_name = employee_data["name"]
        total_break_time = employee_data["total_break_time"] or 0  
        total_allowed_break_time = 30 * employee_data["days_with_break"]  
        break_adherence_percentage = (total_break_time / total_allowed_break_time) * 100
        # print(f"Employee: {employee_name}, Break Adherence: {break_adherence_percentage:.2f}%, Days with Breaks: {employee_data['days_with_break']}")

        formatted_data = {
        'employee_name': employee_name,
        'break_adherence_percentage':break_adherence_percentage
        }
        break_adherence_drilldown.append(formatted_data)
    
    return JsonResponse(break_adherence_drilldown, safe=False)
    
   

def display_page_utilization(region):
    html = ''
    if region == 'APAC':
        html = 'first_app/utilization_apac.html'
    if region == 'EMEA':
        html = 'first_app/utilization_emea.html'
    if region == 'USCA':
        html = 'first_app/utilization_usca.html'
    return html

def get_top_subtask_duration(region):

    highest_hours_by_subtask = Utilization.objects.filter(region=region) \
    .values('subtask') \
    .annotate(total_hours=Sum('duration_hour')) \
    .order_by('-total_hours')[:1]
    return highest_hours_by_subtask

def get_monthly_utlization_rate(current_year, region):
    utilization_data = defaultdict(lambda: defaultdict(int))
    employees_by_month_and_country = defaultdict(lambda: defaultdict(set))

    # Get the current year and the next year for the date range
    start_date = datetime(current_year, 1, 1)
    end_date = datetime(current_year + 1, 1, 1)

    # Filter the TAM_EMEA records for the date range
    utilization = Utilization.objects.filter(shift_start__gte=start_date, shift_start__lt=end_date,region=region)
    # print(utilization)

    # Iterate through the TAM_EMEA records and calculate the total hours worked for each month
    for record in utilization:
        # Get the month of the record's started_date
        month = record.shift_start.month

        # Convert duration_hour to an integer (if it's stored as a string)
        total_hours_worked = float(record.duration_hour)

        # Get the country of the employee
        team = record.team

        # Add the total hours worked to the corresponding month's utilization for the country
        utilization_data[month][team] += total_hours_worked

        # Add the employee to the set of employees for the corresponding month and country
        employees_by_month_and_country[month][team].add(record.name)

    # Calculate the total working hours for each month and country (150 hours per employee)
    total_working_hours_by_month_and_country = {
        month: {team: 150 * len(employees) for team, employees in employees_by_country.items()}
        for month, employees_by_country in employees_by_month_and_country.items()
    }

    # Get the current month
    # current_month = datetime.now().month - 3
    # current_date, current_month, year = actual_first_day_of_the_month()
    current_date, current_month, year = with_last_year_data_first_day_of_the_month()
    

    # Create the missing months and fill them with default values (e.g., 0)
    for month in range(1, current_month + 1):
        month_name = calendar.month_name[month]
        for team in set(record.team for record in utilization):
            # Get the total working hours for the current month and country
            total_working_hours = total_working_hours_by_month_and_country.get(month, {}).get(team, 0)

            # Calculate the utilization rate for the current month and country
            total_hours_worked = utilization_data[month][team]
            if total_hours_worked:
                utilization_rate = (total_hours_worked / total_working_hours) * 100
            else:
                utilization_rate = 0

            # Round off the utilization rate to 2 decimal places
            utilization_rate = round(utilization_rate, 2)

            # Update the utilization_data dictionary with the utilization rate for the month and country
            utilization_data[month_name][team.lower().capitalize()] = utilization_rate

        # Remove the numeric key from the dictionary (optional)
        # del utilization_data[month]

    # Convert the defaultdict to a regular dictionary
    utilization_data_monthly = dict(utilization_data)
    # print(utilization_data_monthly)

    # Convert to JSON and pass it to the template
    utilization_data_monthly_json = json.dumps(utilization_data_monthly)

    highest_util, lowest_util = get_last_month_utilization_rates(current_month,utilization_data_monthly)
    # Replace 0 with a custom message in the context data


    return utilization_data_monthly_json, highest_util, lowest_util


# def get_last_month_high_util_rates(current_month, utilization_data_monthly):
    
#     # Get the last month's name
#     last_month = calendar.month_name[current_month - 5]

#     # Get the utilization rates for the last month (April)
#     utilization_rates_last_month = utilization_data_monthly[last_month]

#     # Sort the utilization rates for the last month in descending order (highest to lowest)
#     sorted_utilization_rates = sorted(utilization_rates_last_month.items(), key=lambda item: item[1], reverse=True)

#     # Extract the first 5 countries with the highest utilization rates
#     first_5_highest_utilization_countries = sorted_utilization_rates[:5]

#     # Convert the first 5 countries with the highest utilization rates to a dictionary
#     first_5_highest_utilization_countries_dict = dict(first_5_highest_utilization_countries)


#     return first_5_highest_utilization_countries_dict

def get_last_month_utilization_rates(current_month, utilization_data_monthly):
    # Get the last month's name
    last_month = calendar.month_name[current_month - 3]
    # print(last_month)

    # Get the utilization rates for the last month (April)
    utilization_rates_last_month = utilization_data_monthly[last_month]

    # Filter teams with utilization rates equal or more than 110%
    high_utilization_teams = {team: rate for team, rate in utilization_rates_last_month.items() if rate >= 110}

    # Filter teams with utilization rates under 99%
    under_utilization_teams = {team: rate for team, rate in utilization_rates_last_month.items() if rate < 99}

    # Sort the high utilization teams based on their utilization rates (from highest to lowest)
    sorted_high_utilization_teams = sorted(high_utilization_teams.items(), key=lambda item: item[1], reverse=True)

    # Sort the under-utilization teams based on their utilization rates (from lowest to highest)
    sorted_under_utilization_teams = sorted(under_utilization_teams.items(), key=lambda item: item[1], reverse=True)

    # Convert the sorted high utilization teams to a dictionary
    sorted_high_utilization_teams_dict = dict(sorted_high_utilization_teams)

    # Convert the sorted under-utilization teams to a dictionary
    sorted_under_utilization_teams_dict = dict(sorted_under_utilization_teams)

    return sorted_high_utilization_teams_dict, sorted_under_utilization_teams_dict




def grouped_by_category(team, region,current_month, current_year):
    # Filter the TAM_EMEA model based on the country and date range
    filtered_data = Utilization.objects.filter(
        team=team,
        shift_start__year=current_year,
        shift_start__month=current_month,
        region=region
    ).values('subtask', 'week').annotate(total_hours=Sum('duration_hour'))


    # Create a dictionary to hold the grouped data
    grouped_category = {}

    # Initialize variables to store the sums of each week
    week_sums = {}

    # Aggregate the total hours for each week for each category
    for category_week in filtered_data:
        subtask = category_week['subtask']
        week = int(category_week['week'].split()[1])  # Extract the numeric week value
        total_hours = float(category_week['total_hours'])

        if subtask not in grouped_category:
            grouped_category[subtask] = {
                f'week_{week}': total_hours,
                'total_hours_all_weeks': total_hours,
            }
        else:
            grouped_category[subtask][f'week_{week}'] = total_hours
            grouped_category[subtask]['total_hours_all_weeks'] += total_hours

        # Calculate the sums of each week
        if f'week_{week}' not in week_sums:
            week_sums[f'week_{week}'] = total_hours
        else:
            week_sums[f'week_{week}'] += total_hours

    # Calculate the total of total_hours_all_weeks
    total_total_hours = sum(category_data['total_hours_all_weeks'] for category_data in grouped_category.values())
    week_sums['total_total_hours'] = total_total_hours
    

    # Compute utilization percentage for each category
    for category, hours_by_week in grouped_category.items():
        total_hours_all_weeks = hours_by_week['total_hours_all_weeks']
        total_percentage_hours = total_hours_all_weeks / total_total_hours
        total_percentage_hours = total_percentage_hours * 100  # Convert to percentage and round to 2 decimal places

        hours_by_week['total_percentage_hours'] = total_percentage_hours

    
    total_percentage_hours = sum(category_data['total_percentage_hours'] for category_data in grouped_category.values())
    week_sums['total_percentage_hours'] = total_percentage_hours

    # Now, you have the week_sums dictionary containing the sums of each week across all categories
    # And the grouped_category dictionary containing the grouped data for each category
    return grouped_category, week_sums



def fil_utilization(request):
    # Retrieve the selected country and date range from the frontend
    selected_team = request.GET.get('team')
    selected_team = html.unescape(selected_team)
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    region = request.GET.get('region')
    region = region.upper()


    from_date = datetime.strptime(from_date, '%Y-%m-%d')
    to_date = datetime.strptime(to_date, '%Y-%m-%d')
    to_date = to_date.replace(hour=23, minute=59, second=59)

    data_for_team = Utilization.objects.filter(
        shift_start__gte=from_date,
        shift_start__lte=to_date,
        team=selected_team,
        region=region
    )


    # Group the data by employee and week
    employee_week_data = data_for_team.values('name', 'team','week').annotate(total_hours=Sum('duration_hour'))

    # Create a dictionary to hold the grouped data
    grouped_data = {}
    

    # Aggregate the total hours for each week for each employee
    # print("employee_week_data")
    # print(employee_week_data)
    for employee_week in employee_week_data:
        name = employee_week['name']
        team = employee_week['team']
        week = int(employee_week['week'].split()[1])  # Extract the numeric week value
        total_hours = float(employee_week['total_hours'])
        
        if name not in grouped_data:
            grouped_data[name] = {
                'team': team,
                f'week_{week}': total_hours,
                'total_hours_all_weeks': total_hours,
            }
        else:
            grouped_data[name][f'week_{week}'] = total_hours
            grouped_data[name]['total_hours_all_weeks'] += total_hours
    
    # print(grouped_data)

    total_week_1 = 0
    total_week_2 = 0
    total_week_3 = 0
    total_week_4 = 0
    total_hours_new = 0
    total_util_percent = 0
    target_hours_per_month = 150
    for name, hours_by_week in grouped_data.items():
        total_hours_all_weeks = hours_by_week['total_hours_all_weeks']
        utilization_percentage = (total_hours_all_weeks / target_hours_per_month) * 100
        utilization_percentage = utilization_percentage  # Round to 2 decimal places

        hours_by_week['utilization_percentage'] = utilization_percentage

        total_week_1 += hours_by_week.get('week_1', 0)
        total_week_2 += hours_by_week.get('week_2', 0)
        total_week_3 += hours_by_week.get('week_3', 0)
        total_week_4 += hours_by_week.get('week_4', 0)
        total_hours_new += hours_by_week['total_hours_all_weeks']
        total_util_percent += hours_by_week['utilization_percentage']
    
    # Calculate the average utilization percentage
    num_employees = len(grouped_data)
    average_utilization_percentage = total_util_percent / num_employees if num_employees != 0 else 0

    grand_total = {
        'total_week_1': total_week_1,
        'total_week_2': total_week_2,
        'total_week_3': total_week_3,
        'total_week_4': total_week_4,
        'total_hours': total_hours_new,
        'average_utilization_percentage': average_utilization_percentage,
    }

    fil_grouped_category, week_sums_total = fil_utilization_category(selected_team,from_date,to_date,region)

    all_keys = fil_grouped_category.keys()
    all_keys_list = list(all_keys)

    return JsonResponse({'grouped_data': grouped_data,'fil_grouped_category': fil_grouped_category,"all_keys":all_keys_list,"week_sums":grand_total,"week_sums_total":week_sums_total}, safe=False)
    

def fil_utilization_category(selected_team,from_date,to_date,region):

    
    # Perform the filtering based on the selected country and date range
    filtered_data = Utilization.objects.filter(
        team=selected_team,
        shift_start__gte=from_date,
        shift_start__lte=to_date, region=region
    ).values('subtask', 'week').annotate(total_hours=Sum('duration_hour'))

    # Create a dictionary to hold the grouped data
    grouped_category = {}
    week_sums = {}

    # Aggregate the total hours for each week for each category
    for category_week in filtered_data:
        subtask = category_week['subtask']
        week = int(category_week['week'].split()[1])  # Extract the numeric week value
        total_hours = float(category_week['total_hours'])

        if subtask not in grouped_category:
            grouped_category[subtask] = {
                f'week_{week}': total_hours,
                'total_hours_all_weeks': total_hours,
            }
        else:
            grouped_category[subtask][f'week_{week}'] = total_hours
            grouped_category[subtask]['total_hours_all_weeks'] += total_hours

        # Calculate the sums of each week
        if f'week_{week}' not in week_sums:
            week_sums[f'week_{week}'] = total_hours
        else:
            week_sums[f'week_{week}'] += total_hours

    # Calculate the total of total_hours_all_weeks
    if grouped_category:
        total_total_hours = sum(category_data['total_hours_all_weeks'] for category_data in grouped_category.values())
        week_sums['total_total_hours'] = total_total_hours


    # Compute utilization percentage for each category
    for category, hours_by_week in grouped_category.items():
        total_hours_all_weeks = hours_by_week['total_hours_all_weeks']
        total_percentage_hours = total_hours_all_weeks / total_total_hours
        total_percentage_hours = total_percentage_hours * 100  # Convert to percentage and round to 2 decimal places

        hours_by_week['total_percentage_hours'] = total_percentage_hours
        
    if grouped_category:
        total_percentage_hours = sum(category_data['total_percentage_hours'] for category_data in grouped_category.values())
        week_sums['total_percentage_hours'] = total_percentage_hours

    return grouped_category, week_sums

def fil_utilization_cat_member(request):
    selected_team = request.GET.get('team')
    selected_team = html.unescape(selected_team)
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    member = request.GET.get('member')
    region = request.GET.get('region')
    region = region.upper()

    filtered_data = Utilization.objects.filter(team=selected_team, name=member, shift_start__date__gte=from_date, shift_start__date__lte=to_date,
    region=region).annotate(truncated_date=TruncDate('shift_start')).values('subtask', 'truncated_date', 'week').annotate(total_hours=Sum('duration_hour'))

    # Create a dictionary to hold the grouped data
    grouped_cat_name = {}
    week_sums = {}

    # Aggregate the total hours for each week for each category
    for category_week in filtered_data:
        subtask = category_week['subtask']
        week = int(category_week['week'].split()[1])  # Extract the numeric week value
        total_hours = float(category_week['total_hours'])

        if subtask not in grouped_cat_name:
            grouped_cat_name[subtask] = {
                f'week_{week}': total_hours,
                'total_hours_all_weeks': total_hours,
            }
        else:
            grouped_cat_name[subtask][f'week_{week}'] = total_hours
            grouped_cat_name[subtask]['total_hours_all_weeks'] += total_hours
        
         # Calculate the sums of each week
        if f'week_{week}' not in week_sums:
            week_sums[f'week_{week}'] = total_hours
        else:
            week_sums[f'week_{week}'] += total_hours

    if grouped_cat_name:
        # Calculate the total of total_hours_all_weeks
        total_total_hours = sum(category_data['total_hours_all_weeks'] for category_data in grouped_cat_name.values())
        week_sums['total_total_hours'] = total_total_hours

    
    # Compute utilization percentage for each category
    for category, hours_by_week in grouped_cat_name.items():
        total_hours_all_weeks = hours_by_week['total_hours_all_weeks']
        total_percentage_hours = total_hours_all_weeks / total_total_hours
        total_percentage_hours = total_percentage_hours * 100  # Convert to percentage and round to 2 decimal places

        hours_by_week['total_percentage_hours'] = total_percentage_hours
    
    if grouped_cat_name:
        total_percentage_hours = sum(category_data['total_percentage_hours'] for category_data in grouped_cat_name.values())
        week_sums['total_percentage_hours'] = total_percentage_hours
    
    all_keys = grouped_cat_name.keys()
    all_keys_list = list(all_keys)

    return JsonResponse({'grouped_cat_name': grouped_cat_name,"all_keys_list":all_keys_list,"week_sums":week_sums})

def category_filter(request):
    category = request.GET.get('category')
    group_category = request.GET.get('group_category')

    if group_category:
        complex_data = json.loads(group_category)
    if category:
        category_list = category.split(',')
    filtered_data = {key: value for key, value in complex_data.items() if key in category_list}
    # Calculate sums and totals for the desired fields
    sums = {'week_1': 0, 'week_2': 0, 'week_3': 0, 'week_4': 0, 'total_hours_all_weeks': 0, 'total_percentage_hours': 0}

    for data in filtered_data.values():
        for key, value in data.items():
            if key in sums:
                sums[key] += value
    
    return JsonResponse({'new_group_category':filtered_data,"new_week_sum":sums})


# def weekly_utilization(request):
#     if request.method == 'GET':
#         country = request.GET.get('country_name')
#         week_name = request.GET.get('week')

#         first_day_of_previous_month, num_month = first_day_of_the_month()
#         last_day_of_previous_month = last_day_of_the_month()
        
#         filtered_data = TAM_EMEA.objects.filter(
#             country=country,
#             week=week_name,
#             started_date__gte=first_day_of_previous_month,
#             started_date__lte=last_day_of_previous_month
#         ).values('category').annotate(total_hours=Sum('duration_hour'))

#         # Prepare the data in the desired format
#         data = []
#         for entry in filtered_data:
#             data.append([entry['category'], entry['total_hours']])

#         return JsonResponse({'dataGroupId': week_name, 'weekly_util': data})
    

def weekly_util(grouped_category):

    weekly_sum_data = []
    for week in ['week_1', 'week_2', 'week_3', 'week_4']:
        week_sum = sum(data.get(week, 0) for data in grouped_category.values())
        weekly_sum_data.append({
            'value': week_sum,
            'groupId': week
        })

    # Create the data for the second format
    drilldown_data = []
    for week in ['week_1', 'week_2', 'week_3', 'week_4']:
        data_group_id = week
        data = []
        for category, values in grouped_category.items():
            week_value = values.get(week, 0)
            if week_value != 0:
                data.append([category, week_value])
        if data:
            drilldown_data.append({
                'dataGroupId': data_group_id,
                'data': data
            })
        
    
    return weekly_sum_data,drilldown_data


def weekly_util_with_country(request):
    if request.method == 'GET':
        country = request.GET.get('country')
        region = request.GET.get('region')
        region = region.upper()
        first_date, current_month, current_year = with_last_year_data_first_day_of_the_month()
        # current_year = datetime.now().year

        grouped_category, week_sums_category = grouped_by_category(country,region,current_month,current_year)

        weekly_sum_data,drilldown_data = weekly_util(grouped_category)
    
    return JsonResponse({"weekly_sum_data_country":weekly_sum_data, "drilldown_data_country":drilldown_data})

def monthly_util_with_team(request):
    if request.method == 'GET':
        team = request.GET.get('team')
        region = request.GET.get('region')
        region = region.upper()
    # first_date, current_month = first_day_of_the_month()
    first_date, current_month, current_year = with_last_year_data_first_day_of_the_month()
    grouped_team_util, week_sums_category = grouped_by_category(team,region,current_month,current_year)


    return JsonResponse({"grouped_team_util":grouped_team_util})

def get_last_day_of_month(first_day_of_month):
    # Get the first day of the next month
    first_day_of_next_month = first_day_of_month.replace(day=28) + timedelta(days=4)
    # Go to the beginning of the current month and subtract one day to get the last day of the current month
    last_day_of_month = first_day_of_next_month - timedelta(days=first_day_of_next_month.day)
    return last_day_of_month

def get_top_5_names_with_highest_duration(region):

    # current_date, current_month, current_year = actual_first_day_of_the_month()
    current_date, current_month, current_year = with_last_year_data_first_day_of_the_month()

    # Calculate the start and end date of the current month
    first_day_of_month = datetime(current_year, current_month, 1)
    last_day_of_month = get_last_day_of_month(first_day_of_month)



    # excluding the subtasks 'Break 1' and 'Break 2'
    top_names = (
        Utilization.objects
        .filter(shift_start__gte=first_day_of_month.date(), shift_start__lt=last_day_of_month.date(), region=region)
        .exclude(subtask__in=['Break 1', 'Break 2'])  # Exclude specific subtasks
        .values('name')
        .annotate(total_duration=Sum('duration_hour'))
        .annotate(utilization_percentage=ExpressionWrapper(
            F('total_duration') / 150.0 * 100, output_field=FloatField()
        ))
        .order_by('-total_duration')[:5]
    )
    return top_names

def performance(request):
    # current_year = datetime.now().year
    # current_date, current_month, current_year = actual_first_day_of_the_month()
    current_date, current_month, current_year = with_last_year_data_first_day_of_the_month()
    department_count = MasterList.objects.values('region').annotate(count=Count('id'))
    overall_count = MasterList.objects.count()

    pieData = tenure('')
    region = ''
    real_current_date, real_current_month, real_current_year = actual_first_day_of_the_month()
    overall_percentage_monthly = get_monthly_overall_attendance_rate(real_current_year)

    overall_quality_metrics, overall_quality_average = overall_quality_percentage()
    overall_avg_accuracy_per_region, overall_avg_percentage_per_month_accuracy, overall_avg_value = performance_overall_accuracy_percentage()

    overall_percentage_service_delivery, overall_average_percentage_service = overall_service_delivery()
    overall_utilization_current_year, overall_utilization_whole_year = performance_overall_utilization_percentage(current_year)

    rax_data_util = overall_rax_utilization()
    prod_rate_local_management_data, prod_unique_functions = prod_rate_comparison_by_local_management()


    value = {"regions_count":department_count,"overall_count":overall_count,
             "tenure_count":pieData,"overall_percentage_monthly":overall_percentage_monthly, "overall_quality_metrics":overall_quality_metrics,
             "overall_percentage_service_delivery":overall_percentage_service_delivery,
             "overall_average_percentage_service":overall_average_percentage_service,
             "overall_quality_percentage":overall_quality_average,
             "rax_data_util":rax_data_util,
             "overall_avg_accuracy_per_region":overall_avg_accuracy_per_region,
             "overall_avg_percentage_per_month_accuracy":overall_avg_percentage_per_month_accuracy,
             "overall_avg_value": overall_avg_value,
             "prod_rate_local_management_data":prod_rate_local_management_data,
             "prod_unique_functions":prod_unique_functions
            #  "overall_utilization_current_year":overall_utilization_current_year,
            #  "overall_utilization_whole_year":overall_utilization_whole_year
             }    
    return render(request,'first_app/performance.html',context=value)

def prod_rate_comparison_by_local_management():
    # Get the current year
    current_year = timezone.now().year

    # Get the month mappings
    month_mapping = month_mappings_complete()

    # Create a list of When clauses for ordering the months from January to December
    month_ordering = [
        When(lower_month=month, then=number)
        for month, number in month_mapping.items()
    ]

    # Query to calculate the average production rates, grouped by month and function
    prod_rate_by_month_function = Productivity.objects.filter(
        year=current_year
    ).annotate(
        lower_month=Lower('month')  # Normalize month to lowercase for case-insensitive comparison
    ).values(
        'lower_month', 'function','region'  # Group by the normalized lowercase month and function
    ).annotate(
        avg_target_prod_rate_hour=Round(Avg('target_prod_rate_hour')),  # Round to whole number
        avg_actual_prod_rate_hr=Round(Avg('actual_prod_rate_hr'))  # Round to whole number
    ).order_by(
        Case(*month_ordering, output_field=IntegerField()),  # Order by the month in January to December sequence
        'function'  # Then order by function
    )
    prod_unique_functions = set(item['function'] for item in prod_rate_by_month_function)

    return list(prod_rate_by_month_function), list(prod_unique_functions)

def performance_overall_accuracy_percentage():

    month_order = {
        'January': 1,
        'February': 2,
        'March': 3,
        'April': 4,
        'May': 5,
        'June': 6,
        'July': 7,
        'August': 8,
        'September': 9,
        'October': 10,
        'November': 11,
        'December': 12
    }

    month_case = Case(
        *[When(month=month, then=order) for month, order in month_order.items()],
        output_field=IntegerField()
    )

    queryset = Quality_Report.objects.filter(accuracy__gt=0).annotate(
        month_order=month_case
    ).values('month', 'region').annotate(
        avg_accuracy=Avg('accuracy')
    ).order_by('month_order', 'region')
    
    # Create a dictionary to store the overall average accuracy per region
    overall_avg_accuracy_per_region = {}
    
    for record in queryset:
        month = record['month']
        region = record['region']
        avg_accuracy = record['avg_accuracy']
        
        # Convert to percentage and format to 2 decimal places
        if avg_accuracy is not None:
            avg_accuracy_percentage = f"{avg_accuracy * 100:.2f}%"
        else:
            avg_accuracy_percentage = "N/A"
        
        # Store the result in the dictionary
        if region not in overall_avg_accuracy_per_region:
            overall_avg_accuracy_per_region[region] = {}

        overall_avg_accuracy_per_region[region][month] = avg_accuracy_percentage


    
    overall_avg_percentage_per_month_accuracy, overall_avg_value = compute_average_percentage_per_month(overall_avg_accuracy_per_region)

    return overall_avg_accuracy_per_region, overall_avg_percentage_per_month_accuracy, overall_avg_value


def compute_average_percentage_per_month(data):
    """
    Computes the average percentage for each month across regions
    and the overall average percentage.

    Args:
        data (dict): A dictionary containing region-wise percentages for each month.

    Returns:
        tuple: A tuple containing:
               - dict: A dictionary with the average percentage for each month.
               - float: The overall average percentage.
    """
    overall_avg_percentage = {}

    # Initialize a dictionary to store the sum of percentages for each month
    month_sums = {month: 0.0 for month in data['APAC']}

    # Iterate through each region
    for region, region_data in data.items():
        for month, percentage in region_data.items():
            # Remove the '%' sign and convert to float
            percentage_value = float(percentage.rstrip('%'))
            # Add the percentage to the corresponding month's sum
            month_sums[month] += percentage_value

    # Calculate the average percentage for each month
    num_regions = len(data)
    for month, total_sum in month_sums.items():
        avg_percentage = total_sum / num_regions
        overall_avg_percentage[month] = f"{avg_percentage:.2f}%"

    # Calculate the overall average percentage
    overall_avg_value = sum(float(value.rstrip('%')) for value in overall_avg_percentage.values()) / len(overall_avg_percentage)

    return overall_avg_percentage, overall_avg_value


def performance_overall_utilization_percentage(current_year):

    # Get all utilization records for the given year
    # records = Utilization.objects.filter(shift_start__year=current_year).values('region','shift_start__month','duration_hour','name')
    records = Utilization.objects.filter(shift_start__year=current_year)

    # Annotate the total duration hour and total employees for each region and month
    annotated_records = records.values('region', 'shift_start__month').annotate(
        total_duration_hour=Sum('duration_hour'),
        total_employees=Count('name', distinct=True)
    )

    overall_utilization_data = {}

    # Loop through each annotated record
    for record in annotated_records:
        region = record['region']
        month = record['shift_start__month']
        total_duration_hour = record['total_duration_hour'] or 0
        total_employees = record['total_employees'] or 0

        # Convert month number to month name (e.g., 1 to "Jan")
        month_name = calendar.month_abbr[month]

        # Calculate overall utilization percentage for the month and region
        target_hours_per_employee = 150

        # Check if total_employees is not zero to avoid division by zero
        if total_employees != 0:
            overall_utilization_percentage = (total_duration_hour / (target_hours_per_employee * total_employees)) * 100
        else:
            overall_utilization_percentage = 0

        # Append the overall percentage for the month and region to the dictionary
        if month_name not in overall_utilization_data:
            overall_utilization_data[month_name] = {}

        overall_utilization_data[month_name][region] = round(overall_utilization_percentage, 2)

    formatted_data = [
        {
            'month': month,
            'APAC': overall_utilization_data[month].get('APAC', 0),
            'EMEA': overall_utilization_data[month].get('EMEA', 0),
            'USCA': overall_utilization_data[month].get('USCA', 0)
        }
        for month in overall_utilization_data.keys()
    ]

    sorted_data = sorted(formatted_data, key=lambda x: get_month_index(x['month']))
    overall_utilization = 0  # Default value if sorted_data is empty
    if sorted_data:
        overall_utilization = sum(sum(month_data[region] for region in ['APAC', 'EMEA', 'USCA']) for month_data in sorted_data) / (len(sorted_data) * 3)
    overall_utilization_whole_year = round(overall_utilization, 2)
    

    return sorted_data, overall_utilization_whole_year

def get_month_index(month_abbr):
    return list(calendar.month_abbr).index(month_abbr)


def get_monthly_overall_attendance_rate(current_year):
    
    monthly_counts = Attendance.objects.filter(
        Q(type='PRESENT') | Q(type='UNPLANNED'),
        att_date__year=current_year
    ).values('att_date__month', 'region').annotate(
        scheduled_count=Sum(
            Case(
                When(type='PRESENT', then=1),
                When(type='UNPLANNED', then=1),
                default=0,
                output_field=IntegerField()
            )
        ),
        present_count=Sum(
            Case(
                When(type='PRESENT', then=1),
                default=0,
                output_field=IntegerField()
            )
        )
    )

    percentage_monthly = []

    for monthly_count in monthly_counts:
        month = monthly_count['att_date__month']
        region = monthly_count['region']
        scheduled_count = monthly_count['scheduled_count']
        present_count = monthly_count['present_count']

        month_name = calendar.month_abbr[month]

        # Avoid division by zero errors
        if scheduled_count == 0:
            percentage = 0
        else:
            percentage = present_count / scheduled_count

        percentage_monthly.append({'month': month_name, 'percentage': percentage, 'region': region})
    return percentage_monthly

def delivery(request, region):
    region = region.upper()
    html_page = display_page_delivery(region)
    return render(request,html_page, context="value")

def display_page_delivery(region):
    html = ''
    if region == 'APAC':
        html = 'first_app/delivery_apac.html'
    if region == 'EMEA':
        html = 'first_app/delivery_emea.html'
    if region == 'USCA':
        html = 'first_app/delivery_usca.html'
    return html

def quality(request, region):

    region = region.upper()
    data_dict_with_total, data_dict_without_total = quality_per_country(region)
    percentage_quality, unique_countries , overall_percentage_data, overall_percentage_per_country = quality_percentage(region)
    overall_percentage = overall_quality_compute(region)

    # print(overall_percentage_data)
    context = {
        'quality_records': data_dict_with_total,
        # 'quality_records_without_total': data_dict_without_total,
        'quality_records_with_percentage': percentage_quality,
        'unique_countries':unique_countries,
        'overall_percentage_data':overall_percentage_data,
        'overall_percentage':overall_percentage,
        'overall_percentage_per_country':overall_percentage_per_country
    }
    # print(percentage_quality)
    html_page = display_page_quality(region)

    return render(request, html_page, context=context)

def quality_per_country(region):

    # current_date, current_month, current_year = with_last_year_data_first_day_of_the_month()
    current_date, current_month, current_year = actual_first_day_of_the_month()
    
    metric_names = ["Bridging Error", "Bridging Transaction Checked", "Reference Error", "Reference Transaction Checked", "Coding Errors", "Coding Transaction Checked"]
    
    metric_patterns = [re.compile(re.escape(metric), re.IGNORECASE) for metric in metric_names]

    quality_records = Quality.objects.filter(
        region=region,
        id_calendar_period__startswith=current_year,
        id_metrics_master__iregex=r'(' + '|'.join(pattern.pattern for pattern in metric_patterns) + r')'
    ).values('id_country', 'id_calendar_period', 'id_metrics_master').annotate(metric_value=Sum('metric_value'))


    data_dict_with_total = {}
    data_dict_without_total = {}

    # Loop through the quality_records and populate the data_dicts
    for entry in quality_records:
        country = entry['id_country']
        metric = entry['id_metrics_master']
        month = convert_to_month_name(entry['id_calendar_period'])
        value = entry['metric_value']

        # Ensure that the value is numeric
        if isinstance(value, (int, float)):
            # Create a new dictionary for the country if it doesn't exist
            if country not in data_dict_with_total:
                data_dict_with_total[country] = {}
            
            # Create a new dictionary for the metric if it doesn't exist
            if metric not in data_dict_with_total[country]:
                data_dict_with_total[country][metric] = {}
            
            # Add the value to the month in the metric dictionary
            data_dict_with_total[country][metric][month] = value

            # Create a new dictionary for the country if it doesn't exist
            if country not in data_dict_without_total:
                data_dict_without_total[country] = {}
            
            # Create a new dictionary for the metric if it doesn't exist
            if metric not in data_dict_without_total[country]:
                data_dict_without_total[country][metric] = {}
            
            # Add the value to the month in the metric dictionary, excluding 'total'
            if month != 'total':
                data_dict_without_total[country][metric][month] = value
    
    # Sort the data by id_country and id_metrics_master
    sorted_data = sorted(quality_records, key=lambda x: (x['id_country'], x['id_metrics_master']))

    # Loop through the sorted_data and populate the data_dicts with the metric names
    for entry in sorted_data:
        country = entry['id_country']
        metric = entry['id_metrics_master']
        
        # Create a new dictionary for the country if it doesn't exist
        if country not in data_dict_with_total:
            data_dict_with_total[country] = {}
        
        # Create a new dictionary for the metric if it doesn't exist
        if metric not in data_dict_with_total[country]:
            data_dict_with_total[country][metric] = {}
        
        # Add the metric name to the metric dictionary
        data_dict_with_total[country][metric]['name'] = metric

        # Create a new dictionary for the country if it doesn't exist
        if country not in data_dict_without_total:
            data_dict_without_total[country] = {}
        
        # Create a new dictionary for the metric if it doesn't exist
        if metric not in data_dict_without_total[country]:
            data_dict_without_total[country][metric] = {}
        
        # Add the metric name to the metric dictionary
        data_dict_without_total[country][metric]['name'] = metric

    # Remove 'total' values from the data_dict_without_total
    for country, metrics in data_dict_without_total.items():
        for metric, months in metrics.items():
            if 'total' in months:
                del data_dict_without_total[country][metric]['total']

    # Calculate the total for each metric for each country in data_dict_with_total
    for country, metrics in data_dict_with_total.items():
        for metric, months in metrics.items():
            total = sum(value for value in months.values() if isinstance(value, (int, float)))
            data_dict_with_total[country][metric]['total'] = total

    return data_dict_with_total, data_dict_without_total


    
def overall_quality_compute(region):
    # Define your metric names
    metric_names = [
        "Bridging Error", "Bridging Transaction Checked",
        "Reference Error", "Reference Transaction Checked",
        "Coding Errors", "Coding Transaction Checked"
    ]

    # Compile regex patterns for case-insensitive matching
    metric_patterns = [re.compile(re.escape(metric), re.IGNORECASE) for metric in metric_names]


    current_year = datetime.now().strftime("%Y")
    current_year_int = int(current_year)
    previous_year_int = current_year_int - 1
    current_year = str(previous_year_int)

   

    overall_totals = Quality.objects.filter(
        region=region,  # Assuming id_country is used for region filtering
        id_calendar_period__startswith=current_year,
        id_metrics_master__iregex=r'(' + '|'.join(pattern.pattern for pattern in metric_patterns) + r')'
    ).aggregate(
        total_errors=Sum(
            Case(
                When(id_metrics_master__iregex=r'(Bridging Error|Reference Error|Coding Errors)', then=F('metric_value')),
                default=Value(0),
                output_field=fields.FloatField(),
            )
        ),
        total_transactions_checked=Sum(
            Case(
                When(id_metrics_master__iregex=r'(Bridging Transaction Checked|Reference Transaction Checked|Coding Transaction Checked)', then=F('metric_value')),
                default=Value(0),
                output_field=fields.FloatField(),
            )
        ),
    )

    # Access the overall aggregated values
    overall_total_errors = overall_totals['total_errors'] or 0
    overall_total_transactions_checked = overall_totals['total_transactions_checked'] or 0

    percentage = 0
    if overall_total_transactions_checked != 0:
        percentage = 1 - (overall_total_errors / overall_total_transactions_checked)
    

    overall_percentage = f"{percentage:.2%}"
    return overall_percentage

def overall_quality_percentage():
    current_date, current_month, current_year = actual_first_day_of_the_month()
    # current_date, current_month, current_year = with_last_year_data_first_day_of_the_month()
    metric_names = ["Bridging Error", "Bridging Transaction Checked", "Reference Error", "Reference Transaction Checked", "Coding Errors", "Coding Transaction Checked"]
    metric_patterns = [re.compile(re.escape(metric), re.IGNORECASE) for metric in metric_names]

    metric_records = Quality.objects.filter(
        id_calendar_period__startswith=current_year,
        id_metrics_master__iregex=r'(' + '|'.join(pattern.pattern for pattern in metric_patterns) + r')'
    ).values('region', 'id_calendar_period').annotate(
        bridging_error=Sum(
            Case(
                When(id_metrics_master__iexact='Bridging Error', then=F('metric_value')),
                default=Value(0),
                output_field=fields.FloatField(),
            )
        ),
        bridging_transaction_checked=Sum(
            Case(
                When(id_metrics_master__iexact='Bridging Transaction Checked', then=F('metric_value')),
                default=Value(0),
                output_field=fields.FloatField(),
            )
        ),
        reference_modification_errors=Sum(
            Case(
                When(id_metrics_master__iexact='Reference Error', then=F('metric_value')),
                default=Value(0),
                output_field=fields.FloatField(),
            )
        ),
        reference_modifications_checked=Sum(
            Case(
                When(id_metrics_master__iexact='Reference Transaction Checked', then=F('metric_value')),
                default=Value(0),
                output_field=fields.FloatField(),
            )
        ),
        coding_errors=Sum(
            Case(
                When(id_metrics_master__iexact='Coding Errors', then=F('metric_value')),
                default=Value(0),
                output_field=fields.FloatField(),
            )
        ),
        coding_transactions_checked=Sum(
            Case(
                When(id_metrics_master__iexact='Coding Transaction Checked', then=F('metric_value')),
                default=Value(0),
                output_field=fields.FloatField(),
            )
        ),
    ).order_by('id_calendar_period')

    
    
    for record in metric_records:
        year_month = record['id_calendar_period']
        formatted_month = datetime.strptime(year_month, '%Y%m').strftime('%b')
        record['id_calendar_period'] = formatted_month
        
        # Check if bridging_transaction_checked is greater than zero
        record['percentage_bridging_error'] = (record['bridging_error'] / record['bridging_transaction_checked']) if record['bridging_transaction_checked'] > 0 else 0
        record['percentage_bridging'] = round((1 - record['percentage_bridging_error']) * 100, 2)

        # Check if reference_modifications_checked is greater than zero
        record['percentage_reference_modification_error'] = (record['reference_modification_errors'] / record['reference_modifications_checked']) if record['reference_modifications_checked'] > 0 else 0
        record['percentage_reference'] = round((1 - record['percentage_reference_modification_error']) * 100, 2)

        # Check if coding_transactions_checked is greater than zero
        record['percentage_coding_error'] = (record['coding_errors'] / record['coding_transactions_checked']) if record['coding_transactions_checked'] > 0 else 0
        record['percentage_coding'] = round((1 - record['percentage_coding_error']) * 100, 2)

        record['overall_average_percentage'] = round(((record['percentage_coding'] + record['percentage_reference'] + record['percentage_bridging']) / 3), 2)

    data_by_month = {}

    for record in metric_records:
        region = record['region']
        month = record['id_calendar_period']
        overall_percentage = record['overall_average_percentage']

        if month not in data_by_month:
            data_by_month[month] = {}

        data_by_month[month][region] = overall_percentage

    # Convert the data to the desired format
    formatted_data = [
        {
            'month': month,
            'APAC': data_by_month[month].get('APAC', 0),
            'EMEA': data_by_month[month].get('EMEA', 0),
            'USCA': data_by_month[month].get('USCA', 0),
        }
       for month in data_by_month.keys()
    ]

    # Calculate the overall average percentage
    overall_percentage = 0
    num_months = len(formatted_data)
    for month_data in formatted_data:
        overall_percentage += (month_data['APAC'] + month_data['EMEA'] + month_data['USCA']) / 3

    overall_percentage /= num_months if num_months != 0 else 1  # Avoid division by zero
    overall_percentage = round(overall_percentage, 2)

    return formatted_data, overall_percentage

def quality_percentage(region):
    
    current_date, current_month, current_year = actual_first_day_of_the_month()
    # current_date, current_month, current_year = with_last_year_data_first_day_of_the_month()
    
    # metric_names = ["Bridging Errors", "Bridging transactions checked", "Reference Modification Errors", "Reference Modifications Checked", "Coding Errors", "Coding transactions checked"]
    metric_names = ["Bridging Error", "Bridging Transaction Checked", "Reference Error", "Reference Transaction Checked", "Coding Errors", "Coding Transaction Checked"]

    metric_patterns = [re.compile(re.escape(metric), re.IGNORECASE) for metric in metric_names]

    metric_records = Quality.objects.filter(
        region=region,
        id_calendar_period__startswith=current_year,
        id_metrics_master__iregex=r'(' + '|'.join(pattern.pattern for pattern in metric_patterns) + r')'
    ).values('id_country', 'id_calendar_period').annotate(
        bridging_error=Sum(
            Case(
                When(id_metrics_master__iexact='Bridging Error', then=F('metric_value')),
                default=Value(0),
                output_field=fields.FloatField(),
            )
        ),
        bridging_transaction_checked=Sum(
            Case(
                When(id_metrics_master__iexact='Bridging Transaction Checked', then=F('metric_value')),
                default=Value(0),
                output_field=fields.FloatField(),
            )
        ),
        reference_modification_errors=Sum(
            Case(
                When(id_metrics_master__iexact='Reference Error', then=F('metric_value')),
                default=Value(0),
                output_field=fields.FloatField(),
            )
        ),
        reference_modifications_checked=Sum(
            Case(
                When(id_metrics_master__iexact='Reference Transaction Checked', then=F('metric_value')),
                default=Value(0),
                output_field=fields.FloatField(),
            )
        ),
        coding_errors=Sum(
            Case(
                When(id_metrics_master__iexact='Coding Errors', then=F('metric_value')),
                default=Value(0),
                output_field=fields.FloatField(),
            )
        ),
        coding_transactions_checked=Sum(
            Case(
                When(id_metrics_master__iexact='Coding Transaction Checked', then=F('metric_value')),
                default=Value(0),
                output_field=fields.FloatField(),
            )
        ),
    )
    if metric_records.exists():
        overall_percentage_per_country = calculate_country_overall_percentage(metric_records)
        unique_countries = sorted(set(entry['id_country'] for entry in metric_records if entry['id_country']))
        new_metrics_record = metric_records
        first_country = min(new_metrics_record, key=lambda x: x['id_country'])['id_country']

        # Filter the records for the first country
        new_data = [record for record in new_metrics_record if record['id_country'] == first_country]


        for record in new_data:
            # Check if bridging_transaction_checked is greater than zero
            if record['bridging_transaction_checked'] > 0:
                record['percentage_bridging_error'] = record['bridging_error'] / record['bridging_transaction_checked']
            else:
                record['percentage_bridging_error'] = 0

            # Check if reference_modifications_checked is greater than zero
            if record['reference_modifications_checked'] > 0:
                record['percentage_reference_modification_error'] = record['reference_modification_errors'] / record['reference_modifications_checked']
            else:
                record['percentage_reference_modification_error'] = 0

            # Check if coding_transactions_checked is greater than zero
            if record['coding_transactions_checked'] > 0:
                record['percentage_coding_error'] = record['coding_errors'] / record['coding_transactions_checked']
            else:
                record['percentage_coding_error'] = 0

        
        total_bridging_errors = metric_records.aggregate(total=Sum('bridging_error'))['total'] or 0
        total_bridging_transactions_checked = metric_records.aggregate(total=Sum('bridging_transaction_checked'))['total'] or 1

        total_reference_modification_errors = metric_records.aggregate(total=Sum('reference_modification_errors'))['total'] or 0
        total_reference_modifications_checked = metric_records.aggregate(total=Sum('reference_modifications_checked'))['total'] or 1


        total_coding_errors = metric_records.aggregate(total=Sum('coding_errors'))['total'] or 0
        total_coding_transactions_checked = metric_records.aggregate(total=Sum('coding_transactions_checked'))['total'] or 1
        
        overall_percentage_bridging = 1 - (total_bridging_errors / total_bridging_transactions_checked) 
        overall_percentage_reference_modification = 1 - (total_reference_modification_errors / total_reference_modifications_checked) 
        overall_percentage_coding = 1- (total_coding_errors / total_coding_transactions_checked) 
        
        overall_percentage_data = {
            'overall_percentage_bridging': f"{overall_percentage_bridging:.2%}",
            'overall_percentage_reference_modification': f"{overall_percentage_reference_modification:.2%}",
            'overall_percentage_coding': f"{overall_percentage_coding:.2%}",
        }


        for entry in new_data:
            entry['id_calendar_period'] = convert_to_month_name(entry['id_calendar_period'])
            entry['percentage_reference_modification'] = 1 - entry['percentage_reference_modification_error'] if entry['percentage_reference_modification_error'] != 0 else (1 if entry['reference_modification_errors'] == 0 and entry['reference_modifications_checked'] > 0 else 0)
            entry['percentage_bridging'] = 1 - entry['percentage_bridging_error'] if entry['percentage_bridging_error'] != 0 else (1 if entry['bridging_error'] == 0 and entry['bridging_transaction_checked'] > 0 else 0)
            entry['percentage_coding'] = 1 - entry['percentage_coding_error'] if entry['percentage_coding_error'] != 0 else (1 if entry['coding_errors'] == 0 and entry['coding_transactions_checked'] > 0 else 0)

            

        data = list(new_data)
        combined_data_list = structured_quality_data(data)
    else:
        # Handle the scenario where there is no data returned from the query
        combined_data_list = []
        unique_countries = []
        overall_percentage_data = {}


    return combined_data_list, unique_countries, overall_percentage_data, overall_percentage_per_country

def calculate_country_overall_percentage(metric_records):
    # Aggregate totals for each country
    country_totals = {}
    
    for record in metric_records:
        country_id = record.get('id_country')

        if country_id not in country_totals:
            country_totals[country_id] = {
                'total_errors': 0,
                'total_checked_transactions': 0
            }

        total_bridging_error = record.get('bridging_error', 0)
        total_reference_modification_errors = record.get('reference_modification_errors', 0)
        total_coding_errors = record.get('coding_errors', 0)
        total_bridging_transactions_checked = record.get('bridging_transaction_checked', 0)
        total_reference_modifications_checked = record.get('reference_modifications_checked', 0)
        total_coding_transactions_checked = record.get('coding_transactions_checked', 0)

        country_totals[country_id]['total_errors'] += (
            total_bridging_error +
            total_reference_modification_errors +
            total_coding_errors
        )

        country_totals[country_id]['total_checked_transactions'] += (
            total_bridging_transactions_checked +
            total_reference_modifications_checked +
            total_coding_transactions_checked
        )

    # Calculate overall percentage for each country
    overall_percentage_data = []

    for country_id, totals in country_totals.items():
        total_errors = totals['total_errors']
        total_checked_transactions = totals['total_checked_transactions']

        if total_checked_transactions > 0:
            overall_percentage = 100 - ((total_errors / total_checked_transactions) * 100)
        else:
            overall_percentage = 0  # Handle division by zero

        overall_percentage_data.append({
            'id_country': country_id,
            'overall_percentage': overall_percentage
        })

    # print(overall_percentage_data)
    return overall_percentage_data

def structured_quality_data(data):
    combined_data_list = []
    for data_entry in data:
        percentage_data = {}

        def format_value(value):
            if float(value).is_integer():
                return "{:.0f}".format(value)
            else:
                return "{:.2f}".format(value)

        # Check for Bridging category
        if data_entry['percentage_bridging_error'] != 0 or data_entry['percentage_bridging'] != 0:
            error_value = data_entry['percentage_bridging_error'] * 100
            total_value = data_entry['percentage_bridging'] * 100

            percentage_data['bridging'] = {
                'error': format_value(error_value),
                'rate': format_value(total_value)
            }

        # Check for Reference category
        if data_entry['percentage_reference_modification_error'] != 0 or data_entry['percentage_reference_modification'] != 0:
            error_value = data_entry['percentage_reference_modification_error'] * 100
            total_value = data_entry['percentage_reference_modification'] * 100

            percentage_data['reference'] = {
                'error': format_value(error_value),
                'rate': format_value(total_value)
            }

        # Check for Coding category
        if data_entry['percentage_coding_error'] != 0 or data_entry['percentage_coding'] != 0:
            error_value = data_entry['percentage_coding_error'] * 100
            total_value = data_entry['percentage_coding'] * 100

            percentage_data['coding'] = {
                'error': format_value(error_value),
                'rate': format_value(total_value)
            }

        combined_data = {**data_entry, 'percentages': percentage_data}
        combined_data_list.append(combined_data)

    return combined_data_list

def quality_percentage_country(request):
    # current_year = datetime.now().strftime("%Y")
    # current_year_int = int(current_year)
    # previous_year_int = current_year_int - 1
    # current_year = str(previous_year_int)

    current_date, current_month, current_year = actual_first_day_of_the_month()
    # current_date, current_month, current_year = with_last_year_data_first_day_of_the_month()
    current_year = str(current_year)

    if request.method == 'GET':

        country = request.GET.get('country')
        region = request.GET.get('region')
        region = region.upper()

        metric_names = ["Bridging Error", "Bridging Transaction Checked", "Reference Error", "Reference Transaction Checked", "Coding Errors", "Coding Transaction Checked"]

        metric_patterns = [re.compile(re.escape(metric), re.IGNORECASE) for metric in metric_names]

        metric_records = Quality.objects.filter(
            region=region,
            id_country=country,
            id_calendar_period__startswith=current_year,
            id_metrics_master__iregex=r'(' + '|'.join(pattern.pattern for pattern in metric_patterns) + r')'
        ).values('id_country', 'id_calendar_period').annotate(
            bridging_error=Sum(
                Case(
                    When(id_metrics_master__iexact='Bridging Error', then=F('metric_value')),
                    default=Value(0),
                    output_field=fields.FloatField(),
                )
            ),
            bridging_transaction_checked=Sum(
                Case(
                    When(id_metrics_master__iexact='Bridging Transaction Checked', then=F('metric_value')),
                    default=Value(0),
                    output_field=fields.FloatField(),
                )
            ),
            reference_modification_errors=Sum(
                Case(
                    When(id_metrics_master__iexact='Reference Error', then=F('metric_value')),
                    default=Value(0),
                    output_field=fields.FloatField(),
                )
            ),
            reference_modifications_checked=Sum(
                Case(
                    When(id_metrics_master__iexact='Reference Transaction Checked', then=F('metric_value')),
                    default=Value(0),
                    output_field=fields.FloatField(),
                )
            ),
            coding_errors=Sum(
                Case(
                    When(id_metrics_master__iexact='Coding Errors', then=F('metric_value')),
                    default=Value(0),
                    output_field=fields.FloatField(),
                )
            ),
            coding_transactions_checked=Sum(
                Case(
                    When(id_metrics_master__iexact='Coding Transaction Checked', then=F('metric_value')),
                    default=Value(0),
                    output_field=fields.FloatField(),
                )
            ),
        )
        unique_countries = sorted(set(entry['id_country'] for entry in metric_records if entry['id_country']))
        new_metrics_record = metric_records
        first_country = min(new_metrics_record, key=lambda x: x['id_country'])['id_country']

        # Filter the records for the first country
        new_data = [record for record in new_metrics_record if record['id_country'] == first_country]


        for record in new_data:
            # Check if bridging_transaction_checked is greater than zero
            if record['bridging_transaction_checked'] > 0:
                record['percentage_bridging_error'] = record['bridging_error'] / record['bridging_transaction_checked']
            else:
                record['percentage_bridging_error'] = 0

            # Check if reference_modifications_checked is greater than zero
            if record['reference_modifications_checked'] > 0:
                record['percentage_reference_modification_error'] = record['reference_modification_errors'] / record['reference_modifications_checked']
            else:
                record['percentage_reference_modification_error'] = 0

            # Check if coding_transactions_checked is greater than zero
            if record['coding_transactions_checked'] > 0:
                record['percentage_coding_error'] = record['coding_errors'] / record['coding_transactions_checked']
            else:
                record['percentage_coding_error'] = 0


        for entry in new_data:
            entry['id_calendar_period'] = convert_to_month_name(entry['id_calendar_period'])
            entry['percentage_reference_modification'] = 1 - entry['percentage_reference_modification_error'] if entry['percentage_reference_modification_error'] != 0 else (1 if entry['reference_modification_errors'] == 0 and entry['reference_modifications_checked'] > 0 else 0)
            entry['percentage_bridging'] = 1 - entry['percentage_bridging_error'] if entry['percentage_bridging_error'] != 0 else (1 if entry['bridging_error'] == 0 and entry['bridging_transaction_checked'] > 0 else 0)
            entry['percentage_coding'] = 1 - entry['percentage_coding_error'] if entry['percentage_coding_error'] != 0 else (1 if entry['coding_errors'] == 0 and entry['coding_transactions_checked'] > 0 else 0)

            
        data = list(new_data)
        combined_data_list = structured_quality_data(data)
        
        return JsonResponse(combined_data_list, safe=False)


def quality_percentage_per_country_bcr(request):

    if request.method == 'GET':
   
        country = request.GET.get('country')
        region = request.GET.get('region')
        region = region.upper()

        first_date, current_month , current_year = actual_first_day_of_the_month()

        # Define metric names and create patterns
        metric_names = ["Bridging Error", "Bridging Transaction Checked", "Reference Error", "Reference Transaction Checked", "Coding Errors", "Coding Transaction Checked"]
        metric_patterns = [re.compile(re.escape(metric), re.IGNORECASE) for metric in metric_names]

        # Filter Quality records based on region, current_year, and metric patterns
        metric_records = Quality.objects.filter(
            region=region,
            id_country=country,
            id_calendar_period__startswith=current_year,
            id_metrics_master__iregex=r'(' + '|'.join(pattern.pattern for pattern in metric_patterns) + r')'
        ).values('id_country').annotate(
            bridging_error=Sum(
                Case(
                    When(id_metrics_master__iexact='Bridging Error', then=F('metric_value')),
                    default=Value(0),
                    output_field=fields.FloatField(),
                )
            ),
            bridging_transaction_checked=Sum(
                Case(
                    When(id_metrics_master__iexact='Bridging Transaction Checked', then=F('metric_value')),
                    default=Value(0),
                    output_field=fields.FloatField(),
                )
            ),
            reference_modification_errors=Sum(
                Case(
                    When(id_metrics_master__iexact='Reference Error', then=F('metric_value')),
                    default=Value(0),
                    output_field=fields.FloatField(),
                )
            ),
            reference_modifications_checked=Sum(
                Case(
                    When(id_metrics_master__iexact='Reference Transaction Checked', then=F('metric_value')),
                    default=Value(0),
                    output_field=fields.FloatField(),
                )
            ),
            coding_errors=Sum(
                Case(
                    When(id_metrics_master__iexact='Coding Errors', then=F('metric_value')),
                    default=Value(0),
                    output_field=fields.FloatField(),
                )
            ),
            coding_transactions_checked=Sum(
                Case(
                    When(id_metrics_master__iexact='Coding Transaction Checked', then=F('metric_value')),
                    default=Value(0),
                    output_field=fields.FloatField(),
                )
            ),
        )

        # Prepare the result data
        result_data = []
        for record in metric_records:
            country_data = {
                'id_country': record['id_country'],
                'bridging_percentage': calculate_percentage(record['bridging_error'], record['bridging_transaction_checked']),
                'reference_percentage': calculate_percentage(record['reference_modification_errors'], record['reference_modifications_checked']),
                'coding_percentage': calculate_percentage(record['coding_errors'], record['coding_transactions_checked']),
            }
            result_data.append(country_data)
    # print(result_data)

    return JsonResponse(result_data, safe=False)

def calculate_percentage(errors, checked_transactions):
    if checked_transactions > 0:
        calculated_percentage = round((errors / checked_transactions) * 100, 2)
        complement_percentage = 100 - calculated_percentage
        return complement_percentage
    else:
        return 0  # Handle division by zero





def convert_to_month_name(id_calendar_period):
    
    # month_number = int(id_calendar_period[-3:])
    # month_name = datetime.strptime(str(month_number), "%m").strftime("%B")

    year = int(id_calendar_period[:4])
    month = int(id_calendar_period[4:])
    
    # Convert the year and month to its corresponding name
    date_obj = datetime(year, month, 1)
    month_name = date_obj.strftime("%B")
    
    return month_name

def display_page_quality(region):
    html = ''
    if region == 'APAC':
        html = 'first_app/quality_apac.html'
    if region == 'EMEA':
        html = 'first_app/quality_emea.html'
    if region == 'USCA':
        html = 'first_app/quality_usca.html'
    return html

def service_delivery(request,region):
    region = region.upper()
    # current_year = datetime.now().year - 1
    actual_date, actual_month, actual_year = actual_first_day_of_the_month()
    # actual_date, actual_month, actual_year = with_last_year_data_first_day_of_the_month()
   
    queryset = Service_Delivery.objects.filter(region=region, processing_period__startswith=actual_year)
    grouped_data_list, overall_percentages, latest_month_percentage, formatted_latest_processing_period, average_percentage_per_month, overall_percentage_dict = service_delivery_per_country(queryset,region)

    late_reason_count, grand_total_delayed = service_late_delivery_count(queryset)
    list_of_unique_countries = service_delivery_list_of_countries(queryset)


    html = display_page_service_delivery(region)
    context = {'service_delivery_data': grouped_data_list, 'overall_percentages': overall_percentages, "late_reason_count":late_reason_count, "grand_total_delayed":grand_total_delayed, 
               "list_of_unique_countries":list(list_of_unique_countries),"latest_month_percentage":latest_month_percentage, "formatted_latest_processing_period":formatted_latest_processing_period,
               "average_percentage_per_month":average_percentage_per_month, "overall_percentage_dict":overall_percentage_dict,"actual_year":actual_year}
    return render(request, html, context)

def service_delivery_bu_code(request):

    if request.method == 'GET':
        bu_code = request.GET.get('bu_code')
        region = request.GET.get('region')
        region = region.upper()
        actual_year = request.GET.get('actual_year')

        # print(bu_code)
        # print(region)
        # print(actual_year)

        queryset = Service_Delivery.objects.filter(
            bu_code=bu_code,
            region=region,
            processing_period__startswith=actual_year
        ).values('country').annotate(
            total_rows=Count('country'),
            greater_than_zero_rows=Count(Case(When(delivery_days__gt=0, then=1), output_field=FloatField()))
        ).order_by('country')

        for entry in queryset:
            total_rows = entry['total_rows']
            greater_than_zero_rows = entry['greater_than_zero_rows']

            if total_rows == 0 or greater_than_zero_rows == 0:
                entry['percentage'] = 100.0
            else:
                entry['percentage'] = round((1 - (greater_than_zero_rows / total_rows)) * 100, 2)

        result_data = list(queryset)

        # print(result_data)

    return JsonResponse({'service_delivery_bu_code_percentage':result_data})






# def service_delivery_per_country(queryset, region):
#     grouped_data = ''
#     if region == 'EMEA':
#         grouped_data = queryset.values('bu_code', 'processing_period').annotate(
#             total_rows=Count('id'),
#             greater_than_zero_rows=Sum(
#                 Case(
#                     When(delivery_days__gt=0, then=Value(1)),
#                     default=Value(0),
#                     output_field=IntegerField(),
#                 ),
#             )
#         )
#     else:
#         # Group by country and processing period
#         grouped_data = queryset.values('country', 'processing_period').annotate(
#             total_rows=Count('id'),
#             greater_than_zero_rows=Sum(
#                 Case(
#                     When(delivery_days__gt=0, then=Value(1)),
#                     default=Value(0),
#                     output_field=IntegerField(),
#                 ),
#             )
#         )

#     # print(grouped_data)
#     # Calculate the percentage for each group
#     for entry in grouped_data:
#         total_rows = entry['total_rows']
#         greater_than_zero_rows = entry['greater_than_zero_rows']

#         if total_rows == 0 or greater_than_zero_rows == 0:
#             entry['percentage'] = 100.0
#         else:
#             entry['percentage'] = round((1 - (greater_than_zero_rows / total_rows)) * 100, 2)

        
#         processing_period_date = datetime.strptime(entry['processing_period'], "%Y%m")
#         entry['processing_period'] = processing_period_date.strftime("%B")

#     ######################################################################################################
#     # Calculate the overall percentage for the entire dataset
#     overall_percentage = 0
#     if grouped_data:
#         overall_total_rows = sum(entry['percentage'] for entry in grouped_data)
#         overall_percentage = overall_total_rows / len(grouped_data)
#         overall_percentage = round(overall_percentage, 2)
    
#     ######################################################################################################   



#     ######################################################################################################
#     # Calculate the overall percentage for the latest month

#     latest_processing_period = queryset.aggregate(latest_processing_period=Max('processing_period'))['latest_processing_period']
#     # Format the latest processing period as 'Mon YYYY'
#     latest_processing_period_date = datetime.strptime(str(latest_processing_period), "%Y%m")
#     formatted_latest_processing_period_with_month = latest_processing_period_date.strftime("%B")
#     formatted_latest_processing_period_with_month_year = latest_processing_period_date.strftime("%b %Y")


#     latest_month_entries = [entry for entry in grouped_data if entry['processing_period'] == formatted_latest_processing_period_with_month]
#     # latest_month_total_rows = sum(entry['total_rows'] for entry in latest_month_entries)
#     # latest_month_greater_than_zero_rows = sum(entry['greater_than_zero_rows'] for entry in latest_month_entries)
#     latest_month_percentage = 0
#     if latest_month_entries:
#         total_percentage = sum(entry['percentage'] for entry in latest_month_entries)
#         latest_month_percentage = total_percentage / len(latest_month_entries)

#     ######################################################################################################

#     grouped_data_list = list(grouped_data)
#     grouped_data_list.sort(key=lambda x: datetime.strptime(x['processing_period'], "%B"))

#     average_percentage_per_month = calculate_overall_percentage_per_month(grouped_data_list)

#     overall_percentage_dict = overall_percentage_per_country_for_year(grouped_data_list, region)

#     return grouped_data_list, overall_percentage, latest_month_percentage, formatted_latest_processing_period_with_month_year, average_percentage_per_month, overall_percentage_dict


def service_delivery_per_country(queryset, region):
    try:
        grouped_data = ''
        if region == 'EMEA':
            grouped_data = queryset.values('bu_code', 'processing_period').annotate(
                total_rows=Count('id'),
                greater_than_zero_rows=Sum(
                    Case(
                        When(delivery_days__gt=0, then=Value(1)),
                        default=Value(0),
                        output_field=IntegerField(),
                    ),
                )
            )
        else:
            # Group by country and processing period
            grouped_data = queryset.values('country', 'processing_period').annotate(
                total_rows=Count('id'),
                greater_than_zero_rows=Sum(
                    Case(
                        When(delivery_days__gt=0, then=Value(1)),
                        default=Value(0),
                        output_field=IntegerField(),
                    ),
                )
            )

        # Calculate the percentage for each group
        for entry in grouped_data:
            try:
                total_rows = entry['total_rows']
                greater_than_zero_rows = entry['greater_than_zero_rows']

                if total_rows == 0 or greater_than_zero_rows == 0:
                    entry['percentage'] = 100.0
                else:
                    entry['percentage'] = round((1 - (greater_than_zero_rows / total_rows)) * 100, 2)

                processing_period_date = datetime.strptime(entry['processing_period'], "%Y%m")
                entry['processing_period'] = processing_period_date.strftime("%B")
            except Exception as e:
                entry['percentage'] = 0  # Fallback value in case of error
                entry['processing_period'] = "Unknown"  # Handle invalid date formats
                print(f"Error processing entry: {entry}. Error: {e}")

        # Calculate the overall percentage for the entire dataset
        overall_percentage = 0
        try:
            if grouped_data:
                overall_total_rows = sum(entry['percentage'] for entry in grouped_data)
                overall_percentage = overall_total_rows / len(grouped_data)
                overall_percentage = round(overall_percentage, 2)
        except Exception as e:
            overall_percentage = 0  # Fallback value
            print(f"Error calculating overall percentage: {e}")

        # Calculate the overall percentage for the latest month
        latest_month_percentage = 0
        formatted_latest_processing_period_with_month_year = ""
        try:
            latest_processing_period = queryset.aggregate(latest_processing_period=Max('processing_period'))['latest_processing_period']
            latest_processing_period_date = datetime.strptime(str(latest_processing_period), "%Y%m")
            formatted_latest_processing_period_with_month = latest_processing_period_date.strftime("%B")
            formatted_latest_processing_period_with_month_year = latest_processing_period_date.strftime("%b %Y")

            latest_month_entries = [entry for entry in grouped_data if entry['processing_period'] == formatted_latest_processing_period_with_month]
            
            if latest_month_entries:
                total_percentage = sum(entry['percentage'] for entry in latest_month_entries)
                latest_month_percentage = total_percentage / len(latest_month_entries)
        except Exception as e:
            latest_month_percentage = 0  # Fallback value
            print(f"Error calculating latest month percentage: {e}")

        # Sort the data and calculate the average percentage per month
        try:
            grouped_data_list = list(grouped_data)
            grouped_data_list.sort(key=lambda x: datetime.strptime(x['processing_period'], "%B"))

            average_percentage_per_month = calculate_overall_percentage_per_month(grouped_data_list)
            overall_percentage_dict = overall_percentage_per_country_for_year(grouped_data_list, region)
        except Exception as e:
            grouped_data_list = []  # Fallback value
            average_percentage_per_month = 0  # Fallback value
            overall_percentage_dict = {}  # Fallback value
            print(f"Error calculating additional data: {e}")

        return grouped_data_list, overall_percentage, latest_month_percentage, formatted_latest_processing_period_with_month_year, average_percentage_per_month, overall_percentage_dict

    except Exception as e:
        print(f"Error in service_delivery_per_country: {e}")
        return [], 0, 0, "", 0, {}


def calculate_overall_percentage_per_month(grouped_data_list):
    # Create a dictionary to store overall percentages for each month
    overall_percentage_per_month = {}

    # Iterate through the grouped data
    for entry in grouped_data_list:
        processing_period_month = entry['processing_period']
        percentage = entry['percentage']

        # Check if the month is already in the dictionary
        if processing_period_month not in overall_percentage_per_month:
            overall_percentage_per_month[processing_period_month] = []

        # Append the percentage to the list for that month
        overall_percentage_per_month[processing_period_month].append(percentage)

    # Calculate the average percentage for each month
    average_percentage_per_month = {}
    for month, percentages in overall_percentage_per_month.items():
        total_percentages = sum(percentages)
        average_percentage = total_percentages / len(percentages)
        average_percentage_per_month[month] = round(average_percentage, 2)

    # Sort the dictionary by month (assuming month names are in proper order)
    sorted_average_percentage_per_month = dict(sorted(average_percentage_per_month.items(), key=lambda x: datetime.strptime(x[0], "%B")))

    return sorted_average_percentage_per_month

def overall_percentage_per_country_for_year(grouped_data_list, region):
    overall_percentage_dict = {}

    # Iterate through each entry in the grouped data list
    for entry in grouped_data_list:
        country = ''
        if region == 'EMEA':
            country = entry['bu_code']
        else:
            country = entry['country']
        percentage = entry['percentage']

        # If the country is not in the dictionary, initialize it
        if country not in overall_percentage_dict:
            overall_percentage_dict[country] = []

        # Append the percentage to the list for that country
        overall_percentage_dict[country].append(percentage)

    # Calculate the average percentage for each country
    for country, percentages in overall_percentage_dict.items():
        total_percentage = sum(percentages) / len(percentages)
        overall_percentage_dict[country] = round(total_percentage, 2)

    return overall_percentage_dict

def service_late_delivery_count(queryset):
    result = queryset.filter(ontime_late='Late').values('late_delivery_reason').annotate(reason_count=Count('late_delivery_reason'))
    grand_total_delayed = sum(item['reason_count'] for item in result)
    late_reason_count = list(result)

    return late_reason_count, grand_total_delayed

def service_delivery_list_of_countries(queryset):
    # Get all unique countries from the queryset
    unique_countries = queryset.values_list('country', flat=True).distinct()
    return unique_countries

def service_late_reason_per_country(request):
    country = request.GET.get('country')
    region = request.GET.get('region')
    region = region.upper()
    # current_year = datetime.now().year - 1
    current_date, current_month, current_year = actual_first_day_of_the_month()
    # current_date, current_month, current_year = with_last_year_data_first_day_of_the_month()
    queryset = Service_Delivery.objects.filter(region=region,country=country, processing_period__startswith=current_year)
    result = queryset.filter(country=country,ontime_late='Late').values('late_delivery_reason').annotate(reason_count=Count('late_delivery_reason'))
    grand_total_delayed = sum(item['reason_count'] for item in result)
    late_reason_count = list(result)
    return JsonResponse({'service_late_reason_country':late_reason_count,"grand_total_delayed":grand_total_delayed})


def display_page_service_delivery(region):
    html = ''
    if region == 'APAC':
        html = 'first_app/service_delivery_apac.html'
    if region == 'EMEA':
        html = 'first_app/service_delivery_emea.html'
    if region == 'USCA':
        html = 'first_app/service_delivery_usca.html'
    return html
    
def overall_service_delivery():
    current_date, current_month, current_year = actual_first_day_of_the_month()
    # current_date, current_month, current_year = with_last_year_data_first_day_of_the_month()

    queryset = Service_Delivery.objects.filter(processing_period__startswith=current_year)

    grouped_data = queryset.values('region', 'country', 'processing_period').annotate(
        total_rows=Count('id'),
        greater_than_zero_rows=Sum(
            Case(
                When(delivery_days__gt=0, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            ),
        )
    )

    grouped_dict = defaultdict(lambda: defaultdict(list))  # Updated to store percentages for each country per region per month
    overall_percentage = defaultdict(float)

    for entry in grouped_data:
        total_rows = entry['total_rows']
        greater_than_zero_rows = entry['greater_than_zero_rows']

        if total_rows == 0 or greater_than_zero_rows == 0:
            percentage = 100.0
        else:
            percentage = round((1 - (greater_than_zero_rows / total_rows)) * 100, 2)

        processing_period_date = datetime.strptime(entry['processing_period'], "%Y%m")
        month_name = processing_period_date.strftime("%b")

        region = entry['region']

        grouped_dict[month_name][region].append(percentage)  # Store percentage for each country

    formatted_data = []
    for month, regions in grouped_dict.items():
        month_data = {'month': month}
        for region, percentages in regions.items():
            average_percentage = sum(percentages) / len(percentages)  # Calculate average percentage for the region per month
            month_data[region] = round(average_percentage, 2)
        formatted_data.append(month_data)

    total_percentage_sum = 0
    for month_data in formatted_data:
        for value in month_data.values():
            try:
                total_percentage_sum += float(value)
            except ValueError:
                pass  # Ignore non-numeric values
    total_percentages_count = sum(len(month_data) - 1 for month_data in formatted_data)

    overall_percentage = round(total_percentage_sum / total_percentages_count, 2)
    print(overall_percentage)


    return formatted_data,overall_percentage




def month_mappings():
    
    month_mapping = {
    'Jan': 1,
    'Feb': 2,
    'Mar': 3,
    'Apr': 4,
    'May': 5,
    'Jun': 6,
    'Jul': 7,
    'Aug': 8,
    'Sep': 9,
    'Oct': 10,
    'Nov': 11,
    'Dec': 12,
    }
    return month_mapping

def rax_utilization(request, region):

    months = [month[:3] for month in month_abbr[1:]]

    region_mapping = {
        'apac': 'LEGACY_APAC PROD',
        'emea': 'LEGACY_EMEA PROD',
        'usca': 'LEGACY_USCA'
    }

    month_mapping = month_mappings()
    region_db = region_mapping.get(region.lower())
    if region_db is None:

        return HttpResponse("Invalid or unsupported region", status=400)

    # Filter queryset based on the provided region
    queryset = Rax_Utilization.objects.filter(region=region_db)
    unique_teams = queryset.order_by('team').values_list('team', flat=True).distinct()
    unique_managers = queryset.order_by('manager').values_list('manager', flat=True).distinct()

    formatted_results_in_average = rax_utilization_in_average(queryset, month_mapping)
    formatted_results_in_hours = rax_utilization_in_hours(queryset, month_mapping)

    # Prepare dictionary with month as key
    formatted_results_by_hours = {}
    for result in formatted_results_in_hours:
        formatted_results_by_hours[result['month']] = result

    
    # Prepare dictionary with month as key
    formatted_results_by_average = {}
    for result in formatted_results_in_average:
        formatted_results_by_average[result['month']] = result

    
    # Calculate averages for each team
    teams_data = rax_team_analyst_utilization(queryset)
    overall_rax_util = overall_rax_utilization_in_average(queryset)
    overall_rax_util_in_hours = overall_rax_utilization_in_hours(queryset)


    html = display_page_rax_utilization(region)
    
    value = {"rax_formatted_results_in_average": formatted_results_by_average, "rax_formatted_results_in_hours": formatted_results_by_hours,"months": months,
             "rax_util_unique_teams":unique_teams, "teams_data":teams_data, "overall_rax_util":overall_rax_util, "overall_rax_util_in_hours":overall_rax_util_in_hours,
             "rax_unique_managers":unique_managers}
        
    return render(request, html, context=value)

def overall_rax_utilization_in_average(queryset):
    # Calculate the overall average of active, idle, and shrinkage
    overall_averages = queryset.aggregate(
        average_active=Avg('c_active'),
        average_idle=Avg('c_idle'),
        average_shrinkage=Avg('c_shrinkages')
    )

    # Convert minutes to hours and divide by 9
    overall_active_percentage = (overall_averages['average_active'] / 60 / 9) * 100 if overall_averages['average_active'] is not None else 0
    overall_idle_percentage = (overall_averages['average_idle'] / 60 / 9) * 100 if overall_averages['average_idle'] is not None else 0
    overall_shrinkage_percentage = (overall_averages['average_shrinkage'] / 60 / 9) * 100 if overall_averages['average_shrinkage'] is not None else 0

    overall_data = {
        'overall_active_percentage': round(overall_active_percentage, 1),
        'overall_idle_percentage': round(overall_idle_percentage, 1),
        'overall_shrinkage_percentage': round(overall_shrinkage_percentage, 1)
    }

    return overall_data

def overall_rax_utilization_in_hours(queryset):
    results_in_hours = queryset.aggregate(
        average_active=Avg('c_active'),
        average_idle=Avg('c_idle'),
        average_shrinkage=Avg('c_shrinkages')
    )
    
    # Convert minutes to hours
    active_hours = results_in_hours['average_active'] / 60 if results_in_hours['average_active'] is not None else 0
    idle_hours = results_in_hours['average_idle'] / 60 if results_in_hours['average_idle'] is not None else 0
    shrinkage_hours = results_in_hours['average_shrinkage'] / 60 if results_in_hours['average_shrinkage'] is not None else 0



    overall_util_in_hours = {
        'overall_active_hours': round(active_hours, 2),
        'overall_idle_hours': round(idle_hours, 2),
        'overall_shrinkage_hours': round(shrinkage_hours, 2)
    }

    return overall_util_in_hours

# def overall_rax_utilization():
#     month_mapping = month_mappings()
#     queryset = Rax_Utilization.objects.all()

#      # Group queryset by month and calculate average of active, idle, and shrinkage
#     results = queryset.values('month').annotate(
#         average_active=Avg('active'),   
#     )

#     sorted_results = sorted(results, key=lambda x: month_mapping.get(x['month'], 0))

#     # Format the results
#     formatted_results_in_average = []
#     for result in sorted_results:
#         formatted_result = {
#             'month': result['month'],
#             'active': f"{result['average_active']*100:.1f}%",
#         }
#         formatted_results_in_average.append(formatted_result)
#     print(formatted_results_in_average)
#     return formatted_results_in_average

def overall_rax_utilization():
    month_mapping = month_mappings()
    
    # Get distinct regions from the database
    regions = Rax_Utilization.objects.values_list('region', flat=True).distinct()

    overall_util_in_hours = []

    for region in regions:
        queryset = Rax_Utilization.objects.filter(region=region)
        results = queryset.values('month').annotate(
            average_active=Avg('c_active'),
        )

        sorted_results = sorted(results, key=lambda x: month_mapping.get(x['month'], 0))

        for result in sorted_results:
            active_hours = result['average_active'] / 60 if result['average_active'] is not None else 0

            month_entry = next((entry for entry in overall_util_in_hours if entry['month'] == result['month']), None)
            if month_entry:
                month_entry[region] = round(active_hours, 2)
            else:
                month_entry = {
                    'month': result['month'],
                    region: round(active_hours, 2),
                }
                overall_util_in_hours.append(month_entry)

    for entry in overall_util_in_hours:
        num_regions = len(regions)
        total_active_hours = sum(entry[region] for region in regions if region in entry)
        overall_active_hours = total_active_hours / num_regions
        entry['active'] = round(overall_active_hours, 2)
        for region in regions:
            if region in entry:
                del entry[region]

    return overall_util_in_hours

def overall_rax_utilization_per_team(request):
    region = request.GET.get('region')

    region_mapping = {
        'apac': 'LEGACY_APAC PROD',
        'emea': 'LEGACY_EMEA PROD',
        'usca': 'LEGACY_USCA'
    }

    month_mapping = month_mappings()
    region_db = region_mapping.get(region.lower())
    if region_db is None:
        return HttpResponse("Invalid or unsupported region", status=400)

    queryset = Rax_Utilization.objects.filter(region=region_db)

     # Group queryset by month and calculate average of active, idle, and shrinkage
    results = queryset.values('month').annotate(
        average_active=Avg('active'),   
    )

    sorted_results = sorted(results, key=lambda x: month_mapping.get(x['month'], 0))

    # Format the results
    formatted_results_in_average = []
    for result in sorted_results:
        formatted_result = {
            'month': result['month'],
            'active': f"{result['average_active']*100:.1f}%",
        }
        formatted_results_in_average.append(formatted_result)
    
    # print(formatted_results_in_average)

    return JsonResponse({"rax_util_per_region": formatted_results_in_average})

def rax_utilization_in_average(queryset, month_mapping):

     # Group queryset by month and calculate average of active, idle, and shrinkage
    results = queryset.values('month').annotate(
        average_active=Avg('active'),
        average_idle=Avg('idle'),
        average_shrinkage=Avg('shrinkage'),
        average_inactive=Avg('inactive'),
        average_meeting=Avg('meeting'),
        average_on_break=Avg('on_break'),
        average_auxiliary=Avg('auxiliary'),
        average_toilet=Avg('toilet'),
        total_headcount=Count('name', distinct=True)
    )

    sorted_results = sorted(results, key=lambda x: month_mapping.get(x['month'], 0))

    # Format the results
    formatted_results_in_average = []
    for result in sorted_results:
        formatted_result = {
            'month': result['month'],
            'active': f"{result['average_active']*100:.1f}%",
            'idle': f"{result['average_idle']*100:.1f}%",
            'shrinkage': f"{result['average_shrinkage']*100:.1f}%",
            'inactive': f"{(result['average_inactive'] / 60 / 9) * 100:.1f}%",  
            'meeting': f"{(result['average_meeting'] / 60 / 9) * 100:.1f}%",      
            'on_break': f"{(result['average_on_break'] / 60 / 9) * 100:.1f}%",    
            'auxiliary': f"{(result['average_auxiliary'] / 60 / 9) * 100:.1f}%",  
            'toilet': f"{(result['average_toilet'] / 60 / 9) * 100:.1f}%", 
            'total_headcount': result['total_headcount']
        }
        formatted_results_in_average.append(formatted_result)
    return formatted_results_in_average

def rax_team_analyst_utilization(queryset):
    teams_data = {}
    for entry in queryset:
        team_name = entry.team
        if team_name not in teams_data:
            teams_data[team_name] = {
                'Team': team_name,
                'active_percentage': 0,
                'active': 0,
                'idle_percentage': 0,
                'idle': 0,
                'shrinkages_percentage': 0,
                'shrinkages': 0,
                'count': 0  # Counter for number of entries
            }
        # Convert string values to numbers and convert minutes to hours
        active = float(entry.c_active) / 60
        idle = float(entry.c_idle) / 60
        shrinkages = float(entry.c_shrinkages) / 60

        active_hours = float(entry.c_active) / 60 / 9  # Assuming 9 working hours per day
        idle_hours = float(entry.c_idle) / 60 / 9
        shrinkages_hours = float(entry.c_shrinkages) / 60 / 9
        # Accumulate values
        teams_data[team_name]['active'] += active
        teams_data[team_name]['idle'] += idle
        teams_data[team_name]['shrinkages'] += shrinkages

        teams_data[team_name]['active_percentage'] += active_hours
        teams_data[team_name]['idle_percentage'] += idle_hours
        teams_data[team_name]['shrinkages_percentage'] += shrinkages_hours
        

        teams_data[team_name]['count'] += 1

    # Calculate average hours for each team
    for team_data in teams_data.values():
        if team_data['count'] > 0:
            team_data['active'] /= team_data['count']
            team_data['idle'] /= team_data['count']
            team_data['shrinkages'] /= team_data['count']

            team_data['active_percentage'] /= team_data['count']
            team_data['active_percentages'] = round(team_data['active_percentage'] * 100, 1)

            team_data['idle_percentage'] /= team_data['count']
            team_data['idle_percentages'] = round(team_data['idle_percentage'] * 100, 1)

            team_data['shrinkages_percentage'] /= team_data['count']
            team_data['shrinkages_percentages'] = round(team_data['shrinkages_percentage'] * 100, 1)

    return list(teams_data.values())


def rax_utilization_in_hours(queryset, month_mapping):

    results_in_hours = queryset.values('month').annotate(
        average_active=Avg('c_active'),
        average_idle=Avg('c_idle'),
        average_shrinkage=Avg('c_shrinkages'),
        average_inactive=Avg('inactive'),
        average_meeting=Avg('meeting'),
        average_on_break=Avg('on_break'),
        average_auxiliary=Avg('auxiliary'),
        average_toilet=Avg('toilet')
    )
    
    sorted_results = sorted(results_in_hours, key=lambda x: month_mapping.get(x['month'], 0))
    
    formatted_results_in_hours = []
    for result in sorted_results:
        formatted_result_in_hours = {
            'month': result['month'],
            'active': round(result['average_active'] / 60, 2),
            'idle': round(result['average_idle'] / 60, 2),
            'shrinkage': round(result['average_shrinkage'] / 60, 2),
            'inactive': round(result['average_inactive'] / 60, 2),
            'meeting': round(result['average_meeting'] / 60, 2),
            'on_break': round(result['average_on_break'] / 60, 2),
            'auxiliary': round(result['average_auxiliary'] / 60, 2),
            'toilet': round(result['average_toilet'] / 60, 2)            
        }
        formatted_results_in_hours.append(formatted_result_in_hours)

    # print(formatted_results_in_hours)
    return formatted_results_in_hours

def rax_util_team(request):
    selected_team = request.GET.get('selected_team')
    region = request.GET.get('region')


    queryset = Rax_Utilization.objects.filter(team=selected_team, region=region)\
        .values('month')\
        .annotate(
            average_active=Avg('active'),
            average_idle=Avg('idle'),
            average_shrinkage=Avg('shrinkage'),
            average_inactive=Avg('inactive'),
            average_meeting=Avg('meeting'),
            average_on_break=Avg('on_break'),
            average_auxiliary=Avg('auxiliary'),
            average_toilet=Avg('toilet'),
            total_headcount=Count('name', distinct=True)
        )
    
    month_mapping = month_mappings()
    
    sorted_results = sorted(queryset, key=lambda x: month_mapping.get(x['month'], 0))

    result = {}
    for entry in sorted_results:
        result[entry['month']] = {
            'month': entry['month'],
            'active': f"{entry['average_active']*100:.1f}%",
            'idle': f"{entry['average_idle']*100:.1f}%",
            'shrinkage': f"{entry['average_shrinkage']*100:.1f}%",
            'inactive': f"{(entry['average_inactive'] / 60 / 9) * 100:.1f}%",  
            'meeting': f"{(entry['average_meeting'] / 60 / 9) * 100:.1f}%",      
            'on_break': f"{(entry['average_on_break'] / 60 / 9) * 100:.1f}%",    
            'auxiliary': f"{(entry['average_auxiliary'] / 60 / 9) * 100:.1f}%",  
            'toilet': f"{(entry['average_toilet'] / 60 / 9) * 100:.1f}%", 
            'total_headcount': entry['total_headcount']
        }

    rax_analysts_data = rax_analyst_utilization(region, selected_team)

    return JsonResponse({"rax_formatted_team": result,"rax_analyst_util":list(rax_analysts_data)})

def rax_analyst_utilization(region, selected_team):
    results = {}

    # Construct the queryset with both region and team filters
    queryset = Rax_Utilization.objects.filter(region=region, team=selected_team)
    for entry in queryset:
        analyst_name = entry.name
        if analyst_name not in results:
            results[analyst_name] = {
                'Name': analyst_name,
                'active_percentage': 0,
                'active': 0,
                'idle_percentage': 0,
                'idle': 0,
                'shrinkages_percentage': 0,
                'shrinkages': 0,
                'count': 0  # Counter for number of entries
            }
        
        active_hours = float(entry.c_active) / 60 / 9  # Assuming 9 working hours per day
        idle_hours = float(entry.c_idle) / 60 / 9
        shrinkages_hours = float(entry.c_shrinkages) / 60 / 9
        
        results[analyst_name]['active'] += active_hours
        results[analyst_name]['idle'] += idle_hours
        results[analyst_name]['shrinkages'] += shrinkages_hours

        results[analyst_name]['active_percentage'] += active_hours
        results[analyst_name]['idle_percentage'] += idle_hours
        results[analyst_name]['shrinkages_percentage'] += shrinkages_hours
        
        results[analyst_name]['count'] += 1

    for result in results.values():
        if result['count'] > 0:
            result['active'] /= result['count']
            result['idle'] /= result['count']
            result['shrinkages'] /= result['count']

            result['active_percentage'] /= result['count']
            result['active_percentages'] = round(result['active_percentage'] * 100, 1)

            result['idle_percentage'] /= result['count']
            result['idle_percentages'] = round(result['idle_percentage'] * 100, 1)

            result['shrinkages_percentage'] /= result['count']
            result['shrinkages_percentages'] = round(result['shrinkages_percentage'] * 100, 1)

    return  results.values()







def rax_util_team_hours(request):
    selected_team = request.GET.get('selected_team')
    region = request.GET.get('region')
    

    queryset = Rax_Utilization.objects.filter(team=selected_team, region=region)

    result = {}
    for entry in queryset:
        result[entry.month] = {
            'month': entry.month,
            'active': round(float(entry.c_active) / 60, 2),
            'idle': round(float(entry.c_idle) / 60, 2),
            'shrinkage': round(float(entry.c_shrinkages) / 60, 2),
            'inactive': round(float(entry.inactive) / 60, 2),
            'meeting': round(float(entry.meeting) / 60, 2),
            'on_break': round(float(entry.on_break) / 60, 2),
            'auxiliary': round(float(entry.auxiliary) / 60, 2),
            'toilet': round(float(entry.toilet) / 60, 2)
        }
        

    return JsonResponse({"rax_formatted_team_hours": result})



def display_page_rax_utilization(region):
    region = region.upper()
    html = ''
    if region == 'APAC':
        html = 'first_app/rax_utilization_apac.html'
    if region == 'EMEA':
        html = 'first_app/rax_utilization_emea.html'
    if region == 'USCA':
        html = 'first_app/rax_utilization_usca.html'
    return html


def quality_report(request, region):
    region = region.upper()

    month_order = {
    'January': 1,
    'February': 2,
    'March': 3,
    'April': 4,
    'May': 5,
    'June': 6,
    'July': 7,
    'August': 8,
    'September': 9,
    'October': 10,
    'November': 11,
    'December': 12
    }
    month_case = Case(
    *[When(month=month, then=order) for month, order in month_order.items()],
    output_field=IntegerField()
     )

    # Aggregate the average accuracy per country for each month
    queryset = Quality_Report.objects.filter(region=region, accuracy__gt=0).annotate(
        month_order=month_case
    ).values('month', 'country').annotate(
        avg_accuracy=Avg('accuracy')
    ).order_by('month_order', 'country')

    parsed_data = [
        {
            'month': record['month'],
            'country': record['country'],
            'avg_accuracy': f"{float(record['avg_accuracy']) * 100:.2f}%" if record['avg_accuracy'] else "N/A"
        }
        for record in queryset
    ]


   # Calculate the overall average accuracy per country
    country_aggregate = {}
    for record in queryset:
        country = record['country']
        avg_accuracy = record['avg_accuracy']
        if country not in country_aggregate:
            country_aggregate[country] = {'total_accuracy': 0, 'count': 0}
        country_aggregate[country]['total_accuracy'] += avg_accuracy
        country_aggregate[country]['count'] += 1

    overall_data = []
    for country, data in country_aggregate.items():
        overall_avg_accuracy = data['total_accuracy'] / data['count']
        overall_data.append({'country': country, 'overall_avg_accuracy': f"{overall_avg_accuracy * 100:.2f}%"})

    # Calculate the overall average accuracy across all records
    overall_avg_accuracy = overall_accuracy_percentage(region)
    overall_avg_accuracy_team = overall_accuracy_by_team(region)


    html = display_page_quality_report(region)
   
    value = {
        "quality_report_averages": list(parsed_data),
        "quality_report_overall_averages": overall_data,
        "overall_avg_accuracy": overall_avg_accuracy,
        "overall_avg_accuracy_team":overall_avg_accuracy_team
    }
        
    return render(request, html, context=value)

def overall_accuracy_percentage(region):
    # Calculate the overall average accuracy across all records
    overall_avg_accuracy = Quality_Report.objects.filter(region=region, accuracy__gt=0).aggregate(avg_accuracy=Avg('accuracy'))['avg_accuracy']
    print(overall_avg_accuracy)
    if overall_avg_accuracy is not None:
        # Convert to percentage and format to 2 decimal places
        overall_avg_accuracy_percentage = f"{overall_avg_accuracy * 100:.2f}%"
        print(overall_avg_accuracy_percentage )
    else:
        overall_avg_accuracy_percentage = "N/A"
    return overall_avg_accuracy_percentage

def overall_accuracy_by_team(region):
    # Get distinct teams for the given region
    teams = Quality_Report.objects.filter(region=region).values_list('team', flat=True).distinct()

    # Calculate average accuracy for each team
    team_avg_accuracies = {}
    for team in teams:
        queryset = Quality_Report.objects.filter(region=region, team=team, accuracy__gt=0)
        avg_accuracy = queryset.aggregate(avg_accuracy=Avg('accuracy'))['avg_accuracy']
        if avg_accuracy is not None:
            team_avg_accuracies[team] = f"{avg_accuracy * 100:.2f}%"
        else:
            team_avg_accuracies[team] = "N/A"
    print(team_avg_accuracies)

    return team_avg_accuracies



def display_page_quality_report(region):
    region = region.upper()
    html = ''
    if region == 'APAC':
        html = 'first_app/quality_report_apac.html'
    if region == 'EMEA':
        html = 'first_app/quality_report_emea.html'
    if region == 'USCA':
        html = 'first_app/quality_report_usca.html'
    return html


def display_page_productivity(region):
    html = ''
    if region == 'APAC':
        html = 'first_app/productivity_apac.html'
    if region == 'EMEA':
        html = 'first_app/productivity_emea.html'
    if region == 'USCA':
        html = 'first_app/productivity_usca.html'
    if region == 'top_management':
        html = 'first_app/productivity_tp.html'
    return html
    
def productivity(request, region):
    actual_volume_processed = ''
    value = {}
    if region == 'top_management':
        actual_volume_processed, unique_functions = top_management()
        productivity_com_data, prod_unique_functions = productivity_rate_comparison()
        prod_rate_com_per_region_data, prod_unique_functions_per_region = prod_rate_comparison_per_region()  
        prod_rate_com_per_task_data = prod_rate_comparison_with_task()

        value = {
            "actual_volume_processed": list(actual_volume_processed),
            "unique_functions": list(unique_functions),
            "productivity_com_data": list(productivity_com_data),
            "prod_unique_functions": list(prod_unique_functions),
            "prod_rate_com_per_region_data": list(prod_rate_com_per_region_data),
            "prod_unique_functions_per_region": list(prod_unique_functions_per_region)
        }
        
    elif region == 'apac' or region == 'emea' or region == 'usca':
        region = region.upper()
        dataProd, prodFunctions = local_management_per_region_prod(region)
        dataVol, volFunctions = local_management_per_region_volume(region)
        dataVolTasks, volTasks, volUniqFunction = local_management_actual_processed_volume(region)
        dataProdTasks, prodTasks, prodTaskFunction = local_management_actual_prod_task(region)
        volManagerData, volManFunction, volManager = local_management_per_manager_volume(region)
        prodManagerData, prodManFunction, prodManager = local_management_prod_rate_per_manager(region)


        value = {"prodData":list(dataProd), 
                 "dataVolume":list(dataVol),
                 "volFunctions":volFunctions,
                 "volUniqFunction":volUniqFunction,
                 "prodFunctions":prodFunctions,
                 "dataVolTasks":list(dataVolTasks),
                 "volTasks":list(volTasks),
                 "dataProdTasks": list(dataProdTasks),
                 "prodTasks":prodTasks,
                 "prodTaskFunction":prodTaskFunction,
                 "volManagerData":list(volManagerData),
                 "volManager":volManager,
                 "volManFunction":volManFunction,
                 "prodManagerData":list(prodManagerData),
                 "prodManFunction":prodManFunction,
                 "prodManager":prodManager
                 
                 }
        
    html = display_page_productivity(region)
    
    return render(request, html, context=value)

def local_management_per_manager_volume(region):
    # Pure function to get the current year
    def get_current_year():
        return timezone.now().year

    # Pure function to create month ordering using When clauses
    def get_month_ordering():
        month_mapping = month_mappings_complete()
        return [When(lower_month=month, then=number) for month, number in month_mapping.items()]

    # Get the current year and month ordering
    current_year = get_current_year()
    month_ordering = get_month_ordering()

    # Retrieve all unique managers for the current year and region in alphabetical order
    all_managers = list(Productivity.objects.filter(
        year=current_year, region=region
    ).values_list('manager', flat=True).distinct().order_by('manager'))

    # Get the first manager alphabetically
    first_manager = all_managers[0] if all_managers else None

    # Return early if no managers are found
    if not first_manager:
        return [], set(), []

    # Query to get per-function totals for the first manager
    result_per_function_manager = Productivity.objects.filter(
        year=current_year, region=region, manager=first_manager
    ).annotate(
        lower_month=Lower('month')  # Annotate the lowercase month
    ).values(
        'lower_month', 'function', 'manager'  # Group by lower_month, function, and manager
    ).annotate(
        total_fte_allocation=Round(Sum('fte_allocation')),  # Round to whole number
        total_task_processed=Round(Sum('task_processed') / Value(1_000_000), 1, output_field=FloatField())  # Round to 1 decimal place in millions
    ).order_by(
        Case(*month_ordering, output_field=IntegerField()),  # Order by custom month ordering
        'function'  # Then order by function
    )

    # Query to get the overall totals for the first manager (without grouping by function)
    result_overall = Productivity.objects.filter(
        year=current_year, region=region, manager=first_manager
    ).annotate(
        lower_month=Lower('month')
    ).values(
        'lower_month', 'manager'  # Group only by lower_month and manager for overall totals
    ).annotate(
        total_fte_allocation=Round(Sum('fte_allocation')),  # Overall FTE allocation
        total_task_processed=Round(Sum('task_processed') / Value(1_000_000), 1, output_field=FloatField())  # Overall task processed
    ).order_by(
        Case(*month_ordering, output_field=IntegerField())
    ).values(
        'lower_month', 'manager', 'total_fte_allocation', 'total_task_processed'
    )

    # Convert result_overall to have 'function' set to 'Overall'
    result_overall = [
        {**item, 'function': 'Overall'} for item in result_overall
    ]

    # Combine per-function-manager results with overall results
    final_result = list(result_per_function_manager) + result_overall

    # Extract unique functions (including 'Overall')
    unique_function = set(item['function'] for item in final_result)

    # Return the final combined result, unique functions, and all managers in alphabetical order
    return final_result, unique_function, all_managers


def local_management_per_manager_volume_click(request):
    manager_clicked = request.GET.get('manager')
    region = request.GET.get('region')
    region = region.upper()


    # Pure function to get the current year
    def get_current_year():
        return timezone.now().year

    # Pure function to create month ordering using When clauses
    def get_month_ordering():
        month_mapping = month_mappings_complete()
        return [When(lower_month=month, then=number) for month, number in month_mapping.items()]

    # Get the current year and month ordering
    current_year = get_current_year()
    month_ordering = get_month_ordering()



    # Retrieve all unique managers for the current year and region in alphabetical order
    all_managers = list(Productivity.objects.filter(
        year=current_year, region=region
    ).values_list('manager', flat=True).distinct().order_by('manager'))


    # Query to get per-function totals for the first manager
    result_per_function_manager = Productivity.objects.filter(
        year=current_year, region=region, manager=manager_clicked
    ).annotate(
        lower_month=Lower('month')  # Annotate the lowercase month
    ).values(
        'lower_month', 'function', 'manager'  # Group by lower_month, function, and manager
    ).annotate(
        total_fte_allocation=Round(Sum('fte_allocation')),  # Round to whole number
        total_task_processed=Round(Sum('task_processed') / Value(1_000_000), 1, output_field=FloatField())  # Round to 1 decimal place in millions
    ).order_by(
        Case(*month_ordering, output_field=IntegerField()),  # Order by custom month ordering
        'function'  # Then order by function
    )


    # Query to get the overall totals for the first manager (without grouping by function)
    result_overall = Productivity.objects.filter(
        year=current_year, region=region, manager=manager_clicked
    ).annotate(
        lower_month=Lower('month')
    ).values(
        'lower_month', 'manager'  # Group only by lower_month and manager for overall totals
    ).annotate(
        total_fte_allocation=Round(Sum('fte_allocation')),  # Overall FTE allocation
        total_task_processed=Round(Sum('task_processed') / Value(1_000_000), 1, output_field=FloatField())  # Overall task processed
    ).order_by(
        Case(*month_ordering, output_field=IntegerField())
    ).values(
        'lower_month', 'manager', 'total_fte_allocation', 'total_task_processed'
    )

    # Convert result_overall to have 'function' set to 'Overall'
    result_overall = [
        {**item, 'function': 'Overall'} for item in result_overall
    ]

    # Combine per-function-manager results with overall results
    vol_manager_data_click = list(result_per_function_manager) + result_overall

    # Extract unique functions (including 'Overall')
    unique_function = list(set(item['function'] for item in vol_manager_data_click))
    
    # Prepare the data to return
    response_data = {
        'vol_manager_data_click': list(vol_manager_data_click),
        'unique_function':unique_function,
        'all_managers':all_managers
    }

    return JsonResponse(response_data, safe=False)

def local_management_per_manager_productivity_click(request):
    manager_clicked = request.GET.get('manager')
    region = request.GET.get('region')
    region = region.upper()


    # Pure function to get the current year
    def get_current_year():
        return timezone.now().year

    # Pure function to create month ordering using When clauses
    def get_month_ordering():
        month_mapping = month_mappings_complete()
        return [When(lower_month=month, then=number) for month, number in month_mapping.items()]

    # Get the current year and month ordering
    current_year = get_current_year()
    month_ordering = get_month_ordering()



    # Retrieve all unique managers for the current year and region in alphabetical order
    all_managers = list(Productivity.objects.filter(
        year=current_year, region=region
    ).values_list('manager', flat=True).distinct().order_by('manager'))


    # Query to get per-function totals for the first manager
    result_per_function_manager = Productivity.objects.filter(
        year=current_year, region=region, manager=manager_clicked
    ).annotate(
        lower_month=Lower('month')  # Annotate the lowercase month
    ).values(
        'lower_month', 'function', 'manager'  # Group by lower_month, function, and manager
    ).annotate(
        avg_target_prod_rate_hour=Round(Avg('target_prod_rate_hour')),  # Average target production rate per hour
        avg_actual_prod_rate_hr=Round(Avg('actual_prod_rate_hr'))  # Average actual production rate per hour
    ).order_by(
        Case(*month_ordering, output_field=IntegerField()),  # Order by custom month ordering
        'function'  # Then order by function
    )


    # Query to get the overall totals for the first manager (without grouping by function)
    result_overall = Productivity.objects.filter(
        year=current_year, region=region, manager=manager_clicked
    ).annotate(
        lower_month=Lower('month')
    ).values(
        'lower_month', 'manager'  # Group only by lower_month and manager for overall totals
    ).annotate(
        avg_target_prod_rate_hour=Round(Avg('target_prod_rate_hour')),  # Average target production rate per hour
        avg_actual_prod_rate_hr=Round(Avg('actual_prod_rate_hr'))  # Average actual production rate per hour
    ).order_by(
        Case(*month_ordering, output_field=IntegerField())
    ).values(
        'lower_month', 'manager', 'avg_target_prod_rate_hour', 'avg_actual_prod_rate_hr'
    )

    # Convert result_overall to have 'function' set to 'Overall'
    result_overall = [
        {**item, 'function': 'Overall'} for item in result_overall
    ]

    # Combine per-function-manager results with overall results
    prod_manager_data_click = list(result_per_function_manager) + result_overall

    # Extract unique functions (including 'Overall')
    unique_function = list(set(item['function'] for item in prod_manager_data_click))

    print(prod_manager_data_click)
    print(unique_function)
    
    # Prepare the data to return
    response_data = {
        'prod_manager_data_click': list(prod_manager_data_click),
        'unique_function':unique_function,
        'all_managers':all_managers
    }

    return JsonResponse(response_data, safe=False)


def local_management_per_manager_volume_click_drilldown(request):
    manager_clicked = request.GET.get('manager')
    region = request.GET.get('region')
    function = request.GET.get('function')
    month = request.GET.get('month')
    
    # Ensure the region is in uppercase
    region = region.upper()

    # Function to capitalize the first letter of the month
    def capitalize_month(month_name):
        return month_name.capitalize()

    # Pure function to get the current year
    def get_current_year():
        return timezone.now().year

    # Pure function to create month ordering using When clauses
    def get_month_ordering():
        month_mapping = month_mappings_complete()  # Assuming month_mappings_complete() is available
        return [When(lower_month=month, then=number) for month, number in month_mapping.items()]

    # Get the current year and month ordering
    current_year = get_current_year()
    month_ordering = get_month_ordering()

    # Capitalize the month name to match the stored format (e.g., 'January' instead of 'january')
    capitalized_month = capitalize_month(month)

    # Query to get the data grouped by team_lead, total_fte_allocation, and total_task_processed
    query = Productivity.objects.filter(
        year=current_year, 
        region=region, 
        manager=manager_clicked,  # Always filter by manager
        month=capitalized_month  # Apply the capitalized month filter
    )

    # If the function is not 'Overall', add the function to the filter
    if function != "Overall" and function:
        query = query.filter(function=function)

    # Group by team_lead and annotate total_fte_allocation and total_task_processed
    result_grouped_by_team_lead = query.annotate(
        lower_month=Lower('month')  # Annotate the lowercase month
    ).values(
         'month',
         # 'team_lead', # Group by lower_month and team_lead
         'team_name'
    ).annotate(
        total_fte_allocation=Round(Sum('fte_allocation')),  # Total FTE allocation
        total_task_processed=Round(Sum('task_processed') / Value(1_000_000), 1, output_field=FloatField())  # Total task processed in millions
    ).order_by(
        Case(*month_ordering, output_field=IntegerField())  # Custom month ordering
    )

    # Prepare the data to return
    response_data = {
        'vol_manager_data_click': list(result_grouped_by_team_lead),  # Data grouped by team_lead
    }

    return JsonResponse(response_data, safe=False)


def local_management_per_manager_productivity_click_drilldown(request):
    manager_clicked = request.GET.get('manager')
    region = request.GET.get('region')
    function = request.GET.get('function')
    month = request.GET.get('month')
    
    # Ensure the region is in uppercase
    region = region.upper()

    # Function to capitalize the first letter of the month
    def capitalize_month(month_name):
        return month_name.capitalize()

    # Pure function to get the current year
    def get_current_year():
        return timezone.now().year

    # Pure function to create month ordering using When clauses
    def get_month_ordering():
        month_mapping = month_mappings_complete()  # Assuming month_mappings_complete() is available
        return [When(lower_month=month, then=number) for month, number in month_mapping.items()]

    # Get the current year and month ordering
    current_year = get_current_year()
    month_ordering = get_month_ordering()

    # Capitalize the month name to match the stored format (e.g., 'January' instead of 'january')
    capitalized_month = capitalize_month(month)

    # Query to get the data grouped by team_lead, total_fte_allocation, and total_task_processed
    query = Productivity.objects.filter(
        year=current_year, 
        region=region, 
        manager=manager_clicked,  # Always filter by manager
        month=capitalized_month  # Apply the capitalized month filter
    )

    # If the function is not 'Overall', add the function to the filter
    if function != "Overall" and function:
        query = query.filter(function=function)

    # Group by team_lead and annotate total_fte_allocation and total_task_processed
    result_grouped_by_team_lead = query.annotate(
        lower_month=Lower('month')  # Annotate the lowercase month
    ).values(
         'month','team_lead' # Group by lower_month and team_lead
    ).annotate(
        avg_target_prod_rate_hour=Round(Avg('target_prod_rate_hour')),  
        avg_actual_prod_rate_hr=Round(Avg('actual_prod_rate_hr'))   
    ).order_by(
        Case(*month_ordering, output_field=IntegerField())  # Custom month ordering
    )

    # Prepare the data to return
    response_data = {
        'prod_manager_data_click_drill': list(result_grouped_by_team_lead),  # Data grouped by team_lead
    }

    return JsonResponse(response_data, safe=False)


def local_management_per_region_prod(region):
    # Pure function to get the current year
    def get_current_year():
        return timezone.now().year

    # Pure function to create month ordering using When clauses
    def get_month_ordering():
        month_mapping = month_mappings_complete()
        return [When(lower_month=month, then=number) for month, number in month_mapping.items()]

    # Get the current year and month ordering
    current_year = get_current_year()
    month_ordering = get_month_ordering()

    # Query to get per-function average production rates
    result_per_function = Productivity.objects.filter(
        year=current_year, region=region
    ).annotate(
        lower_month=Lower('month')  # Normalize month to lowercase for case-insensitive comparison
    ).values(
        'lower_month', 'function'  # Group by lower_month and function
    ).annotate(
        avg_target_prod_rate_hour=Round(Avg('target_prod_rate_hour')),  # Average target production rate
        avg_actual_prod_rate_hr=Round(Avg('actual_prod_rate_hr'))  # Average actual production rate
    ).order_by(
        Case(*month_ordering, output_field=IntegerField()),  # Order by custom month ordering
        'function'  # Then order by function
    )

    # Query to get the overall average production rates (without grouping by function)
    result_overall = Productivity.objects.filter(
        year=current_year, region=region
    ).annotate(
        lower_month=Lower('month')
    ).values(
        'lower_month'  # Group only by lower_month for overall rates
    ).annotate(
        avg_target_prod_rate_hour=Round(Avg('target_prod_rate_hour')),  # Overall average target rate
        avg_actual_prod_rate_hr=Round(Avg('actual_prod_rate_hr'))  # Overall average actual rate
    ).order_by(
        Case(*month_ordering, output_field=IntegerField())
    ).values(
        'lower_month', 'avg_target_prod_rate_hour', 'avg_actual_prod_rate_hr'
    )

    # Convert result_overall to have 'function' set to 'Overall'
    result_overall = [
        {**item, 'function': 'Overall'} for item in result_overall
    ]

    # Combine per-function results with overall results
    final_result = list(result_per_function) + result_overall

    # Extract unique functions (including 'Overall')
    prod_unique_functions = set(item['function'] for item in final_result)

    # Return the final combined result and unique functions
    return final_result, prod_unique_functions

def local_management_per_region_volume(region):
    # Pure function to get the current year
    def get_current_year():
        return timezone.now().year

    # Pure function to create month ordering using When clauses
    def get_month_ordering():
        month_mapping = month_mappings_complete()
        return [When(lower_month=month, then=number) for month, number in month_mapping.items()]

    # Get the current year and month ordering
    current_year = get_current_year()
    month_ordering = get_month_ordering()

    # Query to get per-function totals
    result_per_function = Productivity.objects.filter(
        year=current_year, region=region
    ).annotate(
        lower_month=Lower('month')  # Annotate the lowercase month
    ).values(
        'lower_month', 'function'  # Group by lower_month and function
    ).annotate(
        total_fte_allocation=Round(Sum('fte_allocation')),  # Round to whole number
        total_task_processed=Round(Sum('task_processed') / Value(1_000_000), 1, output_field=FloatField())  # Round to 1 decimal place in millions
    ).order_by(
        Case(*month_ordering, output_field=IntegerField()),  # Order by custom month ordering
        'function'
    )

    # Query to get the overall totals
    result_overall = Productivity.objects.filter(
        year=current_year, region=region
    ).annotate(
        lower_month=Lower('month')
    ).values(
        'lower_month'  # Only group by lower_month for overall totals
    ).annotate(
        total_fte_allocation=Round(Sum('fte_allocation')),  # Overall FTE allocation
        total_task_processed=Round(Sum('task_processed') / Value(1_000_000), 1, output_field=FloatField())  # Overall task processed
    ).order_by(
        Case(*month_ordering, output_field=IntegerField())
    ).values(
        'lower_month', 'total_fte_allocation', 'total_task_processed'
    )

    # Convert result_overall to have 'function' set to 'Overall'
    result_overall = [
        {**item, 'function': 'Overall'} for item in result_overall
    ]

    # Combine per-function results with overall results
    final_result = list(result_per_function) + result_overall

    # Extract unique functions (including 'Overall')
    unique_functions = set(item['function'] for item in final_result)

    # Return the final combined result and unique functions
    return final_result, unique_functions


def local_management_actual_prod_task(region):

    current_year = timezone.now().year

    # Get the month mappings
    month_mapping = month_mappings_complete()

    # Create a list of When clauses for ordering
    month_ordering = [
        When(lower_month=month, then=number) 
        for month, number in month_mapping.items()
    ]

    # First, annotate the queryset with a lowercase version of 'month'
    result = Productivity.objects.filter(
        year=current_year,
        region=region,
        # function='C&B'
    ).annotate(
        lower_month=Lower('month')  # Annotate the lowercase month
    ).values(
        'lower_month', 'tasks', 'function'  # Group by lower_month and task_processed
    ).annotate(
        avg_target_prod_rate_hour=Round(Avg('target_prod_rate_hour')),  # Round to whole number
        avg_actual_prod_rate_hr=Round(Avg('actual_prod_rate_hr'))  # Round to whole number
    ).order_by(
        Case(*month_ordering, output_field=IntegerField()),  # Order by custom month ordering
    )

    # Extract unique task_processed values
    unique_tasks = set(item['tasks'] for item in result)
    unique_funct = set(item['function'] for item in result)
    return result, unique_tasks, unique_funct


def local_management_prod_rate_per_manager(region):
    def get_current_year():
        return timezone.now().year

    # Pure function to create month ordering using When clauses
    def get_month_ordering():
        month_mapping = month_mappings_complete()
        return [When(lower_month=month, then=number) for month, number in month_mapping.items()]

    # Get the current year and month ordering
    current_year = get_current_year()
    month_ordering = get_month_ordering()

    # Retrieve all unique managers for the current year and region in alphabetical order
    all_managers = list(Productivity.objects.filter(
        year=current_year, region=region
    ).values_list('manager', flat=True).distinct().order_by('manager'))

    # Get the first manager alphabetically
    first_manager = all_managers[0] if all_managers else None

    # Return early if no managers are found
    if not first_manager:
        return [], set(), []

    # Query to get per-function totals for the first manager
    result_per_function_manager = Productivity.objects.filter(
        year=current_year, region=region, manager=first_manager
    ).annotate(
        lower_month=Lower('month')  # Annotate the lowercase month
    ).values(
        'lower_month', 'function', 'manager'  # Group by lower_month, function, and manager
    ).annotate(
        avg_target_prod_rate_hour=Round(Avg('target_prod_rate_hour')),  # Average target production rate per hour
        avg_actual_prod_rate_hr=Round(Avg('actual_prod_rate_hr'))  # Average actual production rate per hour
    ).order_by(
        Case(*month_ordering, output_field=IntegerField()),  # Order by custom month ordering
        'function'  # Then order by function
    )

    # Query to get the overall totals for the first manager (without grouping by function)
    result_overall = Productivity.objects.filter(
        year=current_year, region=region, manager=first_manager
    ).annotate(
        lower_month=Lower('month')
    ).values(
        'lower_month', 'manager'  # Group only by lower_month and manager for overall totals
    ).annotate(
        avg_target_prod_rate_hour=Round(Avg('target_prod_rate_hour')),  # Average target production rate per hour
        avg_actual_prod_rate_hr=Round(Avg('actual_prod_rate_hr'))  # Average actual production rate per hour
    ).order_by(
        Case(*month_ordering, output_field=IntegerField())
    ).values(
        'lower_month', 'manager', 'avg_target_prod_rate_hour', 'avg_actual_prod_rate_hr'
    )

    # Convert result_overall to have 'function' set to 'Overall'
    result_overall = [
        {**item, 'function': 'Overall'} for item in result_overall
    ]

    # Combine per-function-manager results with overall results
    final_result = list(result_per_function_manager) + result_overall

    # Extract unique functions (including 'Overall')
    unique_function = set(item['function'] for item in final_result)

    # Return the final combined result, unique functions, and all managers in alphabetical order
    return final_result, unique_function, all_managers
    
    

def local_management_actual_processed_volume(region):
    current_year = timezone.now().year

    # Get the month mappings
    month_mapping = month_mappings_complete()

    # Create a list of When clauses for ordering
    month_ordering = [
        When(lower_month=month, then=number) 
        for month, number in month_mapping.items()
    ]

    # First, annotate the queryset with a lowercase version of 'month'
    result = Productivity.objects.filter(
        year=current_year,
        region=region
        # function='C&B'
    ).annotate(
        lower_month=Lower('month')  # Annotate the lowercase month
    ).values(
        'lower_month', 'tasks','function'  # Group by lower_month and task_processed
    ).annotate(
        total_fte_allocation=Round(Sum('fte_allocation')),  # Round to whole number
        avg_fte_allocation = Avg('fte_allocation')
    ).order_by(
        Case(*month_ordering, output_field=IntegerField()),  # Order by custom month ordering
    )

    # Extract unique task_processed values
    unique_tasks = set(item['tasks'] for item in result)
    unique_funct = set(item['function'] for item in result)
    return result, unique_tasks, unique_funct


    

def top_management():
    # Get the current year
    current_year = timezone.now().year

    # Get the month mappings
    month_mapping = month_mappings_complete()

    # Create a list of When clauses for ordering
    month_ordering = [
        When(lower_month=month, then=number) 
        for month, number in month_mapping.items()
    ]

    # First, annotate the queryset with a lowercase version of 'month'
    result = Productivity.objects.filter(
        year=current_year
    ).annotate(
        lower_month=Lower('month')  # Annotate the lowercase month
    ).values(
        'lower_month', 'function'  # Group by lower_month and function
    ).annotate(
        total_fte_allocation=Round(Sum('fte_allocation')),  # Round to whole number
        total_task_processed=Round(Sum('task_processed') / Value(1_000_000), 1, output_field=FloatField())  # Round to 1 decimal place in millions
    ).order_by(
        Case(*month_ordering, output_field=IntegerField()),  # Order by custom month ordering
        'function'  # Then order by function
    )

    # Extract unique functions
    unique_functions = set(item['function'] for item in result)
    

    # Returning the result
    return result, unique_functions

def month_mappings_complete():
    
    month_mapping = {
    'january': 1,
    'february': 2,
    'march': 3,
    'april': 4,
    'may': 5,
    'june': 6,
    'july': 7,
    'august': 8,
    'september': 9,
    'october': 10,
    'november': 11,
    'december': 12,
    }
    return month_mapping


def productivity_rate_comparison():
    # Get the current year
    current_year = timezone.now().year

    # Get the month mappings
    month_mapping = month_mappings_complete()

    # Create a list of When clauses for ordering the months from January to December
    month_ordering = [
        When(lower_month=month, then=number)
        for month, number in month_mapping.items()
    ]

    # Query to calculate the average production rates, grouped by function and month (case-insensitive)
    productivity_rate_comparison_data = Productivity.objects.filter(
        year=current_year
    ).annotate(
        lower_month=Lower('month')  # Normalize month to lowercase for case-insensitive comparison
    ).values(
        'lower_month', 'function'  # Group by the normalized lowercase month and function
    ).annotate(
        avg_target_prod_rate_hour=Round(Avg('target_prod_rate_hour')),  # Round to whole number
        avg_actual_prod_rate_hr=Round(Avg('actual_prod_rate_hr'))  # Round to whole number
    ).order_by(
        Case(*month_ordering, output_field=IntegerField()),  # Order by the month in January to December sequence
        'function'  # Then order by function
    )

    # Extract unique functions
    prod_unique_functions = set(item['function'] for item in productivity_rate_comparison_data)
    
    return productivity_rate_comparison_data, prod_unique_functions


def prod_rate_comparison_per_region():
    # Get the current year
    current_year = timezone.now().year

    # Get the month mappings
    month_mapping = month_mappings_complete()

    # Create a list of When clauses for ordering the months from January to December
    month_ordering = [
        When(lower_month=month, then=number)
        for month, number in month_mapping.items()
    ]

    # Query to calculate the average production rates, grouped by region, function, and month
    prod_rate_com_per_region_data = Productivity.objects.filter(
        year=current_year
    ).annotate(
        lower_month=Lower('month')  # Normalize month to lowercase for case-insensitive comparison
    ).values(
        'lower_month', 'region', 'function'  # Group by the normalized lowercase month, region, and function
    ).annotate(
        avg_target_prod_rate_hour=Round(Avg('target_prod_rate_hour')),  # Round to whole number
        avg_actual_prod_rate_hr=Round(Avg('actual_prod_rate_hr'))  # Round to whole number
    ).order_by(
        Case(*month_ordering, output_field=IntegerField()),  # Order by the month in January to December sequence
        'region',  # Then order by region
        'function'  # Then order by function
    )

    # Extract unique functions and regions
    prod_unique_functions_per_region = set(item['function'] for item in prod_rate_com_per_region_data)

    return prod_rate_com_per_region_data, prod_unique_functions_per_region


def productivity_per_region_drilleddown(request):
    region = request.GET.get('region')
    month_abbr = request.GET.get('month')
    function = request.GET.get('function')
    year = request.GET.get('year')

    # Map abbreviated month names to full month names
    month_mapping = {
        'Jan': 'January',
        'Feb': 'February',
        'Mar': 'March',
        'Apr': 'April',
        'May': 'May',
        'Jun': 'June',
        'Jul': 'July',
        'Aug': 'August',
        'Sep': 'September',
        'Oct': 'October',
        'Nov': 'November',
        'Dec': 'December'
    }

    # Get the full month name from the abbreviation
    full_month = month_mapping.get(month_abbr)

    # Create month ordering based on full month names
    month_ordering = [
        When(lower_month=month.lower(), then=index)
        for index, month in enumerate(month_mapping.values(), start=1)
    ]

    # Filter the Productivity model based on the provided fields
    prod_rate_com_per_region_data = Productivity.objects.filter(
        year=year,
        region=region,
        function=function,
        month=full_month  # Filter by the full month name
    ).annotate(
        lower_month=Lower('month')  # Normalize month to lowercase for case-insensitive comparison
    ).values(
        'lower_month', 'team_name'  # Replace 'region' with 'team_name'
    ).annotate(
        avg_target_prod_rate_hour=Round(Avg('target_prod_rate_hour')),  # Round to whole number
        avg_actual_prod_rate_hr=Round(Avg('actual_prod_rate_hr'))  # Round to whole number
    ).order_by(
        Case(*month_ordering, output_field=IntegerField()),  # Order by month (January to December sequence)
        'team_name'  # Then order by team_name
    )
   

    return JsonResponse(list(prod_rate_com_per_region_data), safe=False)


def prod_rate_comparison_with_task():
    # Get the current year
    current_year = timezone.now().year

    # Get the month mappings
    month_mapping = month_mappings_complete()

    # Create a list of When clauses for ordering the months from January to December
    month_ordering = [
        When(lower_month=month, then=number)
        for month, number in month_mapping.items()
    ]

    # Query to calculate the average production rates, grouped by month, region, function, and task
    prod_rate_com_with_task_data = Productivity.objects.filter(
        year=current_year
    ).annotate(
        lower_month=Lower('month')  # Normalize month to lowercase for case-insensitive comparison
    ).values(
        'lower_month', 'region', 'function', 'tasks'  # Group by the normalized lowercase month, region, function, and task
    ).annotate(
        avg_target_prod_rate_hour=Round(Avg('target_prod_rate_hour')),  # Round to whole number
        avg_actual_prod_rate_hr=Round(Avg('actual_prod_rate_hr'))  # Round to whole number
    ).order_by(
        Case(*month_ordering, output_field=IntegerField()),  # Order by the month in January to December sequence
        'region',  # Then order by region
        'function'  # Then order by function
    )
    
    prod_unique_functions_per_task = set(item['function'] for item in prod_rate_com_with_task_data)
   
    return prod_rate_com_with_task_data, prod_unique_functions_per_task


    
    
    


    




   





 


