from django import forms
from django.forms import SelectDateWidget


class ReportFiltersForm(forms.Form):
    start_date = forms.DateField(input_formats='%Y,%m,%d',required=False)
    end_date = forms.DateField(input_formats='%Y,%m,%d',required=False)
    class Meta:
        fields=('start_date','end_date')
        widgets={
            'start_date': forms.DateTimeInput(attrs=dict(type='datetime-local')),
            'end_date': forms.DateTimeInput(attrs=dict(type='datetime-local')),
        }