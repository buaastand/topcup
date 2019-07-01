
from django import forms


class RegisterForm(forms.Form):
    stu_id = forms.CharField(required=True)
    name = forms.CharField(required=True)
    department = forms.CharField(required=True)
    major = forms.CharField(required=True)
    enroll_time = forms.DateField(required=True)
    phone = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    birthdate = forms.DateField(required=True)
    degree = forms.IntegerField(required=True)
    address = forms.CharField(required=True)
    password = forms.CharField(required=True,min_length=8)



class LoginForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(required=True)
    type = forms.IntegerField(required=True)

class ModifyPwdForm(forms.Form):
    pwd1 = forms.CharField(required=True,min_length=8)
    pwd2 = forms.CharField(required=True,min_length=8)