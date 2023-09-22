import decimal
from django.db import models
from accounts.models import MyUser
from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
from django.utils.datetime_safe import datetime
from django.contrib.sessions.models import Session

# Create your models here.
 

class Cart(models.Model):
    user = models.OneToOneField("accounts.MyUser", verbose_name="User",related_name="cart" , on_delete=models.CASCADE,null=True,)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True,)
    # total = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    updated = models.DateTimeField(auto_now=True)
    count = models.PositiveIntegerField(default=0)
    session=models.ForeignKey(Session, on_delete=models.CASCADE,null=True)
    coupon = models.ForeignKey('coupons.UserCoupon',related_name='user_cart',on_delete = models.SET_NULL,null=True)
    
    
    def __str__(self):
        return f"This cart contains {self.count} items and its cost is {self.total}"
    def get_absolute_url(self):
        return self.id
    @property
    def total(self):
        total = decimal.Decimal(0)
        itemlist = self.items.all()
        for item in itemlist:
            total += decimal.Decimal(item.item_total) - decimal.Decimal(item.item_offer_discount)
        return total
    @property
    def final_total(self):
        return self.total - decimal.Decimal(self.coupon_discount)
    @property
    def total_no_discount(self):
        total_no_discount = 0
        itemlist = self.items.all()
        for item in itemlist:
            total_no_discount += item.item_total
        return total_no_discount
    
    @property
    def total_discount_given(self):
        total_discount_given = decimal.Decimal(0.00)
        itemlist = self.items.all()
        for item in itemlist:
            total_discount_given += decimal.Decimal(item.item_offer_discount)
        return total_discount_given

    @property
    def count(self):
        count = self.items.all().count()
        return count
    @property
    def coupon_discount(self):
        if self.coupon is not None:
            main_coupon = self.coupon.coupon
            disc_type = main_coupon.discount_type
            if disc_type == 'Percentage':
                coupon_discount = decimal.Decimal(self.total)*decimal.Decimal(main_coupon.discount_percent_value/100)
                coupon_discount = round(coupon_discount,2)
                if coupon_discount > main_coupon.max_discount_amount:
                    coupon_discount = main_coupon.max_discount_amount
                return coupon_discount
            if disc_type == 'Amount':
                coupon_discount = main_coupon.discount_amount_value
                return coupon_discount
        else:
            coupon_discount = 0.00
            return coupon_discount


class cartItem(models.Model):
    game=models.ForeignKey("products.Game", verbose_name="Game", on_delete=models.CASCADE,related_name='cartitems',null=False,blank=False)
    cart = models.ForeignKey("cart.Cart", verbose_name="cart", on_delete=models.CASCADE,related_name='items')
    updated  = models.DateTimeField(auto_now=True)
    quantity = models.IntegerField(default=1,null=False,blank=False)
    def __str__(self):
        return f"This item is {self.game.title} and its cost is {self.game.base_price}"
    
    def get_absolute_url(self):
        return self.id
    
    @property
    def item_total(self):
        item_total = self.quantity*self.game.base_price
        return item_total

    @property
    def item_offer_discount(self):
        if self.game.discount_status != "None":
            item_offer_discount = self.quantity*self.game.base_price - (self.quantity*self.game.discounted_price)
        else:
            item_offer_discount = 0.00
        return item_offer_discount
    
    @property
    def item_offer_discounted_price(self):
        if self.game.discount_status != 'None':
            item_offer_discounted_price = self.game.discounted_price*self.quantity
        else:
            item_offer_discounted_price = self.game.base_price*self.quantity
        return item_offer_discounted_price
    




