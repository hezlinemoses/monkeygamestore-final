
from django import forms
from django.forms import ModelForm
from .models import Coupon

class CouponCreateForm(ModelForm):
    duration_enable = forms.ChoiceField(choices=(('Yes','Yes'),('No','No')),widget=forms.RadioSelect,label='Enable Duration')
    class Meta:
        model = Coupon
        fields = [
            'duration_enable',
            'coupon_code',
            'discount_type',
            'duration_enable',
            'coupon_type',
            'discount_percent_value',
            'discount_amount_value',
            'min_purchase_amount',
            'max_discount_amount',
            'max_usage_limit',
            'max_usage_per_user_limit',
            'valid_from',
            'valid_till',
            'order_no'
        ]
        widgets = {
            'valid_from': forms.DateTimeInput(attrs=dict(type='datetime-local')),
            'valid_till': forms.DateTimeInput(attrs=dict(type='datetime-local')),
            
        }
        # exclude = ['status','usage_count','start_job_id','end_job_id','force_disable']

    def __init__(self, *args, **kwargs):
        super(CouponCreateForm, self).__init__(*args, **kwargs)
        self.fields['coupon_type'].widget.attrs.update({'onchange':'change_coupon_type()'})
        self.fields['discount_type'].widget.attrs.update({'onchange':'change_discount_type()'})
        self.fields['duration_enable'].widget.attrs.update({'onchange':'change_enable_duration()'})
        self.fields['discount_percent_value'].widget.attrs.update({'onfocusout':'discount_percent_validation()'})
        self.fields['valid_from'].widget.attrs.update({'onchange':'change_valid_till_coupon()'})
        self.fields['max_usage_limit'].widget.attrs.update({"onfocusout":"validation(this.id)"})
        self.fields['max_usage_per_user_limit'].widget.attrs.update({"onfocusout":"validation(this.id)"})
        self.fields['min_purchase_amount'].widget.attrs.update({"onfocusout":"validation(this.id)"})
        self.fields['max_discount_amount'].widget.attrs.update({"onfocusout":"validation(this.id)"})
        self.fields['order_no'].widget.attrs.update({'onfocusout':'check_order()'})


class CouponEditForm(ModelForm):
    class Meta:
        model = Coupon
        fields = [
            
            'coupon_code',
            'discount_type',
            'coupon_type',
            'discount_percent_value',
            'discount_amount_value',
            'min_purchase_amount',
            'max_discount_amount',
            'max_usage_limit',
            'max_usage_per_user_limit',
            'valid_from',
            'valid_till',
            'order_no'
        ]
        widgets = {
            'valid_from': forms.DateTimeInput(attrs=dict(type='datetime-local')),
            'valid_till': forms.DateTimeInput(attrs=dict(type='datetime-local')),
            
        }

    def __init__(self,coupon, *args, **kwargs):
        super(CouponEditForm, self).__init__(*args, **kwargs)
        print(f"----------------------------------------------------{coupon.coupon_code}---------------------------------------------")
        if coupon.status == 'Expired':
            self.fields['coupon_type'].disabled = True
            self.fields['order_no'].disabled=True
            self.fields['coupon_code'].disabled=True
            self.fields['discount_type'].disabled = True
            self.fields['discount_percent_value'].disabled = True
            self.fields['valid_from'].disabled = True
            self.fields['valid_till'].disabled = True
            self.fields['max_usage_limit'].disabled = True
            self.fields['max_usage_per_user_limit'].disabled = True
            self.fields['min_purchase_amount'].disabled = True
            self.fields['max_discount_amount'].disabled = True
        elif coupon.status == 'Upcoming' or coupon.status == 'Active':
            self.fields['coupon_type'].widget.attrs.update({'onchange':'change_coupon_type()'})
            self.fields['order_no'].widget.attrs.update({'onfocusout':'check_order()'})
            self.fields['discount_type'].widget.attrs.update({'onchange':'change_discount_type()'})
            self.fields['discount_percent_value'].widget.attrs.update({'onfocusout':'discount_percent_validation()'})
            if coupon.status == 'Active':
                self.fields['valid_from'].disabled=True
            try:
                self.fields['valid_from'].widget.attrs.update({'onchange':'change_valid_till_coupon()'})
            except:
                pass
            self.fields['max_usage_limit'].widget.attrs.update({"onfocusout":"validation(this.id)"})
            self.fields['max_usage_per_user_limit'].widget.attrs.update({"onfocusout":"validation(this.id)"})
            self.fields['min_purchase_amount'].widget.attrs.update({"onfocusout":"validation(this.id)"})
            self.fields['max_discount_amount'].widget.attrs.update({"onfocusout":"validation(this.id)"})



        if coupon.coupon_type == 'Specific Order':
            del self.fields['valid_till']
            del self.fields['valid_from']
        if coupon.valid_from is None and coupon.coupon_type == 'Normal' and coupon.status == 'Active':
            print('+++++++++++++++++++++++++++++++++++++++++++++ datetimeinput form-control flatpickr-input')
            del self.fields['valid_from']
            del self.fields['valid_till']

        
        
           