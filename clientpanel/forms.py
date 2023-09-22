from django import forms
from django.core.validators import MinLengthValidator,MaxLengthValidator


class VerifyForm(forms.Form):
    code = forms.CharField(max_length=6, required=True, help_text='Enter code')

class otpForm(forms.Form):
    phone = forms.CharField( max_length=10, required=True,
    validators=[MinLengthValidator(10),MaxLengthValidator(10)])
    

