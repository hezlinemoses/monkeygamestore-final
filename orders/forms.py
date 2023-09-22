from dataclasses import fields
from email.policy import default
from random import choices
from crispy_forms.layout import Div, Field
from django import forms

from accounts.models import UserAddress
from .models import Order, ShippingAddress,BillingAddress
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit
from crispy_forms.bootstrap import InlineRadios




class ShippingAddressForm(forms.Form):
    save_address = forms.BooleanField(required=False)
    class Meta:
        model = ShippingAddress
        fields = ('line_1','line_2','first_name','last_name','locality','district','state','country','city','Landmark','pincode','phone','save_address',)

class BillingAddressForm(forms.ModelForm):
    save_address = forms.BooleanField(required=False)
    class Meta:
        model = BillingAddress
        fields = ('line_1','line_2','first_name','last_name','locality','district','state','country','city','Landmark','pincode','phone','save_address')
    

       

class OrderStatusChangeForm(forms.ModelForm):
    
    class Meta:
        model = Order
        fields = ('status'),

    def __init__(self, id, *args, **kwargs):
        super(OrderStatusChangeForm, self).__init__(*args, **kwargs)
        order = Order.objects.get(id=id)
        if order.status == 'Pending Payment':
            self.fields['status'] = forms.ChoiceField(choices = (("Pending Payment","Pending Payment"),("Payment failed","Payment failed"),("Processing","Processing"),("Completed","Completed"),("Cancelled","Cancelled")), required=False)
        elif order.status == 'Payment failed':
            self.fields['status'] = forms.ChoiceField(choices = (("Payment failed","Payment failed"),), required=False)
        elif order.status == 'Processing':
            self.fields['status'] = forms.ChoiceField(choices = (("Processing","Processing"),("Completed","Completed"),("Cancelled","Cancelled")), required=False)
        elif order.status == 'Completed':
            self.fields['status'] = forms.ChoiceField(choices = (("Completed","Completed"),), required=False)
        elif order.status == 'Cancelled':
            self.fields['status'] = forms.ChoiceField(choices = (("Cancelled","Cancelled"),), required=False)


class PaymentMethod(forms.Form):
    CHOICES = (('Wallet','Wallet'),('Paypal','Paypal'),('Razorpay','Razorpay'))
    payment_method = forms.ChoiceField(choices=CHOICES,widget=forms.RadioSelect,)

    class Meta:
        fields=('payment_method')

class AddressMethodForm(forms.Form):
    CHOICES = (('Saved Address','Saved Address'),('New Address','New Address'))
    address_method = forms.ChoiceField(choices=CHOICES,widget=forms.RadioSelect,label='Please select an option for your billing address',initial='Saved Address')
    class Meta:
        fields=('address_method')
    
    def __init__(self,request,*args, **kwargs):
        super(AddressMethodForm, self).__init__(*args, **kwargs)
        check = request.user.address.all().count()
        if check < 1:
            self.fields['address_method'].choices = (('New Address','New Address'),)
        else:
            self.fields['address_method'].choices = (('New Address','New Address'),('Saved Address','Saved Address'))

class SavedAddressSelectForm(forms.Form):
    
    saved_addresses = forms.ModelChoiceField(queryset=None,required=False,widget=forms.RadioSelect,)
    
    class Meta:
        fields = ('saved_addresses',)

    def __init__(self, request, *args, **kwargs):
        super(SavedAddressSelectForm, self).__init__(*args, **kwargs)
        self.fields['saved_addresses'].queryset = UserAddress.objects.filter(user = request.user)
        for address in request.user.address.all()[:1]:
            id=address.id
        self.fields['saved_addresses'].initial = UserAddress.objects.get(id=id)
        