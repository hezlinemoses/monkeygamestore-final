
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from accounts.models import MyUser, UserAddress
from django import forms


class SignUpForm(UserCreationForm):
    

    class Meta:
        model = MyUser
        fields = ('username','phone', 'email', 'password1', 'password2',)

        

class UserAddressForm(ModelForm):
    
    class Meta:
        model = UserAddress
        # fields = ("__all__")
        fields = ('first_name','last_name','line_1','line_2','locality','district','state','country','city','Landmark','pincode','phone',)
        

class UsernameChangeForm(forms.ModelForm):

        class Meta:
            model = MyUser
            fields = ('username',)
    
    # username = forms.CharField(
    #     max_length=100,
    #     validators=[username_validator,MinLengthValidator(2),ProhibitNullCharactersValidator],)
        
        
        

class UserEmailchangeForm(forms.ModelForm):

    class Meta:
        model = MyUser
        fields = ('email',)

class UserPhoneChangeForm(forms.ModelForm):

    class Meta:
        model = MyUser
        fields = ('phone',)


class UserPasswordChangeForm(UserCreationForm):
    model = MyUser
    fields = ('password1','password2')