__author__ = 'Eddie'

from django import forms

class RegisterForm(forms.Form):
    username = forms.CharField(label="Username")
    email = forms.EmailField(label="Email Address")
    password = forms.CharField(widget=forms.PasswordInput(), label="Password")
    first_name = forms.CharField(label="First Name")
    last_name = forms.CharField(label="Last Name")

