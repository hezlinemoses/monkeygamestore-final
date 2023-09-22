import uuid
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin,AbstractUser
from accounts.managers import MyUserManager

from accounts.validators import username_validator
from django.core.validators import MinLengthValidator,ProhibitNullCharactersValidator,RegexValidator


# Create your models here.


class MyUser(AbstractBaseUser,PermissionsMixin):
    wallet = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    id = models.UUIDField(
        verbose_name="User id",
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        blank=False,
        null=False
    )
    username = models.CharField(
        verbose_name="Username",
        max_length=100,
        blank=False,
        null=False,
        unique=True,
        validators=[username_validator,MinLengthValidator(2),ProhibitNullCharactersValidator],
        # help_text=("Between 5-20 characters. Alphabets, numbers and @ . + - _ characters."),
        error_messages={
            'unique':("A user with that username already exists")
        }
    )
    email = models.EmailField(
        verbose_name="Email",
         max_length=254,
         unique=True,
         blank=False,
         null=False,
         error_messages={
            'unique' : ("A user with this email already exists")
         }
    )

    first_name = models.CharField(
        verbose_name="First Name",
        max_length=50,
        blank=True,
        null=True,
        # validators=[RegexValidator(regex=r'^[a-zA-Z ]+$',message="Only alphabets and space", code="Invalid name")],
        # help_text=("Only Alphabets"),
        )
    
    last_name = models.CharField(
        verbose_name="Last Name",
        max_length=50,
        blank=True,
        null=True,
        # validators=[RegexValidator(regex=r'^[a-zA-Z ]+$',message="Only alphabets and space", code="Invalid name")],
        # help_text=("Only Alphabets!!")
        )
    
    phone = models.CharField(
        max_length=10,
        null=False,
        blank=False,
        unique=True,
        validators=[MinLengthValidator(10),ProhibitNullCharactersValidator,RegexValidator(regex=r'^[0-9]+$',message='Enter a valid phone number',code='invalid_phone_number')],
        error_messages={
            'unique': ("A user with this phone number already exists")
        },
    )
    
    USERNAME_FIELD = 'email'
    is_blocked = models.BooleanField(default=False)
    is_customer = models.BooleanField(default = False)         #enabled after verification
    is_verified = models.BooleanField(default=False)           #enabled after verification
    is_staff = models.BooleanField(default=False)
    is_active =models.BooleanField(default=True)               #for blocking users                    
    is_superuser = models.BooleanField(default=False)
    objects = MyUserManager()

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        # return reverse("customer_detail", args={self.id})
        return self.id

    



class Address(models.Model):
    
    IN = "India"

    COUNTRY_CHOICES = (
        (IN, 'India'),
    )

    STATE_CHOICES = (("Andhra Pradesh","Andhra Pradesh"),("Arunachal Pradesh ","Arunachal Pradesh "),("Assam","Assam"),("Bihar","Bihar"),("Chhattisgarh","Chhattisgarh"),("Goa","Goa"),("Gujarat","Gujarat"),("Haryana","Haryana"),("Himachal Pradesh","Himachal Pradesh"),("Jammu and Kashmir ","Jammu and Kashmir "),("Jharkhand","Jharkhand"),("Karnataka","Karnataka"),("Kerala","Kerala"),("Madhya Pradesh","Madhya Pradesh"),("Maharashtra","Maharashtra"),("Manipur","Manipur"),("Meghalaya","Meghalaya"),("Mizoram","Mizoram"),("Nagaland","Nagaland"),("Odisha","Odisha"),("Punjab","Punjab"),("Rajasthan","Rajasthan"),("Sikkim","Sikkim"),("Tamil Nadu","Tamil Nadu"),("Telangana","Telangana"),("Tripura","Tripura"),("Uttar Pradesh","Uttar Pradesh"),("Uttarakhand","Uttarakhand"),("West Bengal","West Bengal"),("Andaman and Nicobar Islands","Andaman and Nicobar Islands"),("Chandigarh","Chandigarh"),("Dadra and Nagar Haveli","Dadra and Nagar Haveli"),("Daman and Diu","Daman and Diu"),("Lakshadweep","Lakshadweep"),("National Capital Territory of Delhi","National Capital Territory of Delhi"),("Puducherry","Puducherry"))

    

    first_name = models.CharField(
        verbose_name="First Name",
        max_length=50,
        blank=False,
        null=False,
        )
    
    last_name = models.CharField(
        verbose_name="Last Name",
        max_length=50,
        blank=False,
        null=False,
        )

    line_1 =models.CharField(
        verbose_name="Line 1",
        blank=False,
        null=False,
        max_length=150,
    )
    
    line_2 = models.CharField(
        verbose_name="Line 2",
        max_length=150,
        blank=True,
        null=True,
    )

    locality =models.CharField(
        verbose_name="Locality",
        max_length=50,
        null=False,
        blank=False
        )

    city = models.CharField(
        verbose_name="City",
        max_length=100,
        null=False,
        blank=False
        )
    
    district = models.CharField(
        verbose_name="District",
        max_length=100,
        null=False,
        blank=False
        )

    state = models.CharField(
        verbose_name="State",
        max_length=100,
        null=False,
        blank=False,
        choices = STATE_CHOICES
        )
    
    country = models.CharField(
        verbose_name="Country",
        max_length=100,
        null=False,
        blank=False,
        choices = COUNTRY_CHOICES,
        )

    pincode = models.CharField(
        verbose_name="PINCODE",
        max_length=6,
        null=False,
        blank=False,
        validators=[ProhibitNullCharactersValidator,RegexValidator(regex=r'^[0-9]+$',message='Enter a valid pincode',code='invalid_pin_code')],
    )

    Landmark = models.CharField(max_length=100, blank=True, null = True)

    phone = models.CharField(
        max_length=10,
        null=False,
        blank=False,
        validators=[MinLengthValidator(10),ProhibitNullCharactersValidator,RegexValidator(regex=r'^[0-9]+$',message='Enter a valid phone number',code='invalid_phone_number')],
       )

    def __str__(self):
        return f'''{self.first_name.capitalize()} {self.last_name.capitalize()},
        {self.line_1.capitalize()},
        {self.district.capitalize()},
        {self.state.capitalize()},
        {self.country.capitalize()},
        pincode: {self.pincode},
        Ph: {self.phone}
        '''
    class Meta:
        abstract = True

    


class UserAddress(Address):
    user = models.ForeignKey("accounts.MyUser", verbose_name="User Id", on_delete=models.CASCADE,related_name='address',null='True')
    
  

    def get_absolute_url(self):
        return self.id
