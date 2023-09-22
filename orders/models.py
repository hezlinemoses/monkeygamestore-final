
from datetime import datetime
import decimal
from email.policy import default
from random import choices
from django.db import models
from accounts.models import Address
from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
# Create your models here.


class BillingAddress(Address):
    user = models.ForeignKey("accounts.MyUser", verbose_name="User Id", on_delete=models.CASCADE,related_name='billingaddress',null=True,blank=True)
    def get_absolute_url(self):
        return self.id


class ShippingAddress(Address):
    user = models.ForeignKey("accounts.MyUser", verbose_name="User Id", on_delete=models.CASCADE,related_name='shippingaddress')
    
    def get_absolute_url(self):
        return self.id


class Order(models.Model):
    STATUS_CHOICES = (
        ("Pending Payment","Pending Payment"),
        ("Payment failed","Payment failed"),
        ("Processing","Processing"),
        ("Completed","Completed"),
        ("Cancelled","Cancelled"),
        ("Refunded","Refunded"),
        )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False,)
    user = models.ForeignKey("accounts.MyUser", verbose_name='User', on_delete=models.CASCADE,related_name='orders')
    # total = models.DecimalField(default=0.00, max_digits=20, decimal_places=2,verbose_name='Total',)
    itemcount = models.PositiveIntegerField(default=0)
    is_hidden = models.BooleanField(default=False)
    shipping_address = models.ForeignKey("orders.ShippingAddress", verbose_name="Order Address", on_delete=models.CASCADE,null=True,)
    billing_address = models.ForeignKey("orders.BillingAddress", verbose_name="Billing Address", on_delete=models.CASCADE,null=True,)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    payment_method = models.CharField(choices = (("Razorpay","Razorpay"),("Paypal","Paypal"),("Wallet","Wallet")), null = True,max_length = 20)
    applied_coupon = models.ForeignKey("coupons.UserCoupon",related_name = 'applied_orders',on_delete = models.DO_NOTHING,null = True)
    coupon_code = models.CharField(max_length=100,null=True)
    coupon_discount = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    db_total = models.DecimalField(default=0.00,max_digits=20, decimal_places=2)
    
    def get_absolute_url(self):
        return self.id
    
    def __str__(self):
        return f"This order contains {self.itemcount} items and thier costis {self.total}"
    
    @property
    def is_refundable(self):
        if self.status == 'Completed':
            if self.created_at + timedelta(days=7) >= timezone.now():
                return True
            else:
                return False
        else:
            return False
    
    @property
    def total(self):
        total = decimal.Decimal(0)
        for item in self.items.all():
            total = total + decimal.Decimal(item.item_total)
        if self.coupon_code is not None:
            total = total - self.coupon_discount
        return total
    
    @property
    def total_defore_coupon(self):
        total = decimal.Decimal(0)
        for item in self.items.all():
            total = total + decimal.Decimal(item.item_total)
        return total

    @property
    def total_before_discount(self):
        total_before_discount = decimal.Decimal(0)
        for item in self.items.all():
            total_before_discount = decimal.Decimal(total_before_discount) + decimal.Decimal(item.item_total_before_discount)
        return total_before_discount
    
    @property
    def total_discount_given(self):
        total_discount_given = decimal.Decimal(0)
        for item in self.items.all():
            total_discount_given = decimal.Decimal(total_discount_given) + decimal.Decimal(item.item_offer_discount_given)
        
        return total_discount_given

    

class OrderItem(models.Model):
    game = models.ForeignKey("products.Game", verbose_name="Game", on_delete=models.SET_NULL,null=True,related_name = 'order_items')
    title = models.CharField(max_length=100,)
    item_thumbnail = models.ImageField(upload_to ='thumbnail/',null=True)
    order = models.ForeignKey("orders.Order", verbose_name="Order", related_name="items",on_delete = models.CASCADE)
    item_price = models.DecimalField(verbose_name='Item Price',default=0.00, max_digits=20, decimal_places=2)
    item_offer_discount_given= models.DecimalField(verbose_name='Offer Discount',default=0.00, max_digits=20, decimal_places=2)
    item_offer_discount_percentage = models.IntegerField(default = 0,null = True)
    item_offer_discount_status = models.CharField(max_length = 100, null = True)
    item_offer_discount_name = models.CharField(max_length = 100,null = True)
    quantity = models.IntegerField(default=1)
    def __str__(self):
        return f"This order item contains {self.game.title} and its cost is {self.item_price}"
    
    def get_absolute_url(self):
        return self.id
    @property
    def item_total(self):
        item_total = (self.item_price*self.quantity)-self.item_offer_discount_given
        return item_total

    @property
    def item_total_before_discount(self):
        item_total_before_discount = self.item_price*self.quantity
        return item_total_before_discount

    
@receiver(post_save, sender=OrderItem)
def update_order(sender,instance, **kwargs):
    instance.order.itemcount += instance.quantity
    instance.order.updated_at = datetime.now()
    instance.order.save()
