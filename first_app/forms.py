from django import forms
from django.contrib.auth.forms import AuthenticationForm

class LoginForm(AuthenticationForm):
    pass



class UploadExcelForm(forms.Form):
    excel_file = forms.FileField()