from email.policy import default
from time import timezone
from unicodedata import decimal
from django.utils.timezone import now
import datetime
from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from offerss.models import CategoryOffer


# Create your models here.


class Category(models.Model):
    
    name = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        unique=True,
    )
    description = models.CharField(
        max_length=500,
        null = True,
        blank = True
    )
    slug = models.SlugField(max_length=100, unique=True)

    is_active = models.BooleanField(default = True)
    
    parent_category = models.ForeignKey("self", verbose_name="Parent Category", on_delete=models.CASCADE,related_name="sub_categories", blank = True, null = True)

    discount_status = models.BooleanField(default=False)

    def save(self,*args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    def get_absolute_url(self):
        # return reverse("model_detail", kwargs={"pk": self.pk})
        return self.slug
    
    def __str__(self):
        return self.name


class Platform(models.Model):
    PT_CHOICES = [
    ('Windows', 'Windows'),
    ('MAC-OS', 'MAC-OS'),
    ]

    name = models.CharField(max_length=10,choices=PT_CHOICES,unique=True)



class Specification(models.Model):
    platform = models.ForeignKey("products.Platform", verbose_name="Platform", on_delete=models.SET_NULL, related_name="specs",null=True)
    game = models.ForeignKey("products.Game", verbose_name="Game",on_delete=models.CASCADE,related_name="games",null = True)
    min_os = models




class Game(models.Model):
   
    categories = models.ManyToManyField("products.Category", verbose_name="Categories",blank = False,related_name="games",)
    # platforms = models.ManyToManyField("products.Platform",verbose_name="Platforms", related_name="games")
    title = models.CharField(
        max_length=200,
        null=False,
        blank=False,
    )
    is_active = models.BooleanField(default=True)                                   #---------for soft delete ----- will not be shown to user and  but will be in order histories
    is_discountable = models.BooleanField(default=True)
    base_price = models.IntegerField(null= False, blank=False)
    max_quantity = models.IntegerField(default=10)
    main_banner = models.ImageField(upload_to ='mainbanner/', default=None)
    thumbnail = models.ImageField(upload_to ='thumbnail/',default = None)
    uploaded_on = models.DateTimeField( auto_now=False, auto_now_add=True,)
    updated_on = models.DateTimeField(auto_now=True, auto_now_add=False)
    salecount = models.PositiveIntegerField(default=0)
    discount_status = models.CharField(max_length=100,choices=(('None','None'),('Product Discount','Product Discount'),('Category Discount','Category Discount')),default='None')
    discounted_price = models.DecimalField(null = True,decimal_places = 2, max_digits=20)
    discount_name = models.CharField(max_length = 100,default="None",null = True)
    discount_percentage = models.IntegerField(default=0,null = True)
    discount_end_date = models.DateTimeField(null = True)
    def __str__(self):
        return self.title
        
    def get_absolute_url(self):
        return self.id

    @property
    def discount(self):
        if self.discount_status == 'Product Discount':
            self.discounted_price = self.base_price - round(self.base_price*(self.product_offer.discount_percentage/100),2)
            self.discount_name = self.product_offer.name
            self.discount_percentage = self.product_offer
            self.save()
        elif self.discount_status == 'Category Discount':

            game_categories = self.categories.all()
            highest_discount_percentage = 0
            for category in game_categories:

                try:
                    if CategoryOffer.objects.filter(category=category,status= 'Ongoing').exists():
                        offer = CategoryOffer.objects.get(category=category,status= 'Ongoing')

                        if offer.discount_percentage > highest_discount_percentage:
                            highest_discount_percentage = offer.discount_percentage
                            discount_name = offer.name
                except:
                    pass
            self.discounted_price = self.base_price - round(self.base_price*(highest_discount_percentage/100),2)
            self.discount_name = discount_name
            self.discount_percentage = highest_discount_percentage
            self.save()
        else:
            self.discounted_price = None
            self.discount_name = None
            self.discount_percentage = None
            self.save()
            


class GameDescription(models.Model):
    game = models.ForeignKey("products.Game", verbose_name="Game", on_delete=models.CASCADE, related_name="descriptions")
    heading = models.CharField(max_length=100, null= False, blank = False)
    description = models.CharField(max_length=700, null = False, blank = False)
    def __str__(self):
        return self.description
        
    def get_absolute_url(self):
        return self.id
    


class GameMedia(models.Model):
    game = models.ForeignKey("products.Game", verbose_name="Game", on_delete=models.CASCADE,related_name="medias")
    slideimage = models.ImageField(upload_to ='gameslideshow/',default=None)

    def get_absolute_url(self):
        return self.id






    
