from datetime import timezone
from django import forms
from django.forms import DateInput, ModelForm
from django.utils import timezone
from offerss.models import CategoryOffer, ProductOffer
from products.models import Category





class CategoryOfferCreateForm(forms.ModelForm):
   
    class Meta:
        model = CategoryOffer
        fields = ('category','name','valid_from','valid_till','discount_percentage')
        widgets = {
            'valid_from': forms.DateTimeInput(attrs=dict(type='datetime-local')),
            'valid_till': forms.DateTimeInput(attrs=dict(type='datetime-local')),
            
        }
    def __init__(self, *args, **kwargs):
        super(CategoryOfferCreateForm, self).__init__(*args, **kwargs)
        self.fields['valid_from'].widget.attrs.update({'onchange':"change_date()",})
        self.fields['discount_percentage'].widget.attrs.update({'onfocusout':"change_disc_percent()",})
        self.fields['category'].widget.attrs.update({'onchange':"change_category()",})
        self.fields['category'].queryset = Category.objects.filter(parent_category__isnull = True,)

class CategoryOfferEditForm(forms.ModelForm):
   
    class Meta:
        model = CategoryOffer
        fields = ('category','name','valid_from','valid_till','discount_percentage')
        widgets = {
            'valid_from': forms.DateTimeInput(attrs=dict(type='datetime-local')),
            'valid_till': forms.DateTimeInput(attrs=dict(type='datetime-local')),
            
        }
    def __init__(self,id, *args, **kwargs):
        super(CategoryOfferEditForm, self).__init__(*args, **kwargs)
        offer = CategoryOffer.objects.get(id = id)
        if offer.status == 'Ongoing':
            self.fields['category'].disabled = True
            self.fields['valid_from'].disabled = True
            self.fields['discount_percentage'].disabled = True
        if offer.status == 'Expired':
            self.fields['category'].disabled = True
            self.fields['valid_from'].disabled = True
            self.fields['valid_till'].disabled = True
            self.fields['discount_percentage'].disabled = True
            self.fields['name'].disabled = True
            
        self.fields['valid_from'].widget.attrs.update({'onchange':"change_date()"})
        self.fields['category'].widget.attrs.update({'onchange':"change_category()"})
        self.fields['discount_percentage'].widget.attrs.update({'onfocusout':"change_disc_percent()",})
        self.fields['category'].queryset = Category.objects.filter(parent_category__isnull = True,)


class ProductOfferCreateForm(forms.ModelForm):

    class Meta:
        model = ProductOffer
        fields = ('game','name','valid_from','valid_till','discount_percentage')

        widgets = {
            'valid_from': forms.DateTimeInput(attrs=dict(type='datetime-local')),
            'valid_till': forms.DateTimeInput(attrs=dict(type='datetime-local')),
            
        }

    def __init__(self, *args, **kwargs):
        super(ProductOfferCreateForm, self).__init__(*args, **kwargs)
        self.fields['valid_from'].widget.attrs.update({'onchange':"change_date_game()",})
        self.fields['game'].widget.attrs.update({'onchange':"change_product()",})
        self.fields['discount_percentage'].widget.attrs.update({'onfocusout':"change_disc_percent()",})
        
class ProductOfferEditForm(forms.ModelForm):
   
    class Meta:
        model = ProductOffer
        fields = ('game','name','valid_from','valid_till','discount_percentage')
        widgets = {
            'valid_from': forms.DateTimeInput(attrs=dict(type='datetime-local')),
            'valid_till': forms.DateTimeInput(attrs=dict(type='datetime-local')),
            
        }
    def __init__(self,id, *args, **kwargs):
        super(ProductOfferEditForm, self).__init__(*args, **kwargs)
        offer = ProductOffer.objects.get(id = id)
        if offer.status == 'Ongoing':
            self.fields['game'].disabled = True
            self.fields['valid_from'].disabled = True
            self.fields['discount_percentage'].disabled = True
        if offer.status == 'Expired':
            self.fields['game'].disabled = True
            self.fields['valid_from'].disabled = True
            self.fields['valid_till'].disabled = True
            self.fields['discount_percentage'].disabled = True
            self.fields['name'].disabled = True
            
        self.fields['valid_from'].widget.attrs.update({'onchange':"change_date_game()"})
        self.fields['game'].widget.attrs.update({'onchange':"change_product()"})
        self.fields['discount_percentage'].widget.attrs.update({'onfocusout':"change_disc_percent()",})