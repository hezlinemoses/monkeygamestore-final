from django.db import models
from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.validators import MaxValueValidator
from redis import Redis
from rq_scheduler import Scheduler
import coupons.tasks
# Create your models here.


scheduler = Scheduler(connection=Redis(host='redis_service'))

class Coupon(models.Model):
    custom_user = models.ForeignKey("accounts.MyUser",on_delete=models.CASCADE,null=True,related_name="generated_coupons")
    coupon_code = models.CharField(max_length=100,unique=True,null=False,blank=False,)
    discount_type = models.CharField(choices=(("Percentage","Percentage"),("Amount","Amount")),max_length=20,null = False,blank = False)
    coupon_type = models.CharField(choices=(("Normal","Normal"),("Specific Order","Specific Order")),max_length=20,help_text="Select specific order if you want to tie this to a particular order.")
    discount_percent_value= models.PositiveIntegerField(null=True,blank=True,validators=[MaxValueValidator(60)])
    discount_amount_value = models.PositiveIntegerField(null=True,blank=True)
    min_purchase_amount = models.PositiveIntegerField(null=False,blank=False,verbose_name='Minimum Purchase Amount')
    max_discount_amount = models.PositiveIntegerField(null=True,blank=True,verbose_name='Maximum Discount Amount')
    max_usage_limit = models.PositiveIntegerField(null=True,blank=True,verbose_name='Usage Limit')
    max_usage_per_user_limit = models.PositiveIntegerField(null=True,blank=True,verbose_name='Usage Limit Per User')
    valid_from = models.DateTimeField(null=True,blank=True)
    valid_till = models.DateTimeField(null=True,blank=True)
    order_no = models.PositiveIntegerField(null=True,blank = True)
    status = models.CharField(choices=(("Upcoming","Upcoming"),("Active","Active"),("Expired","Expired")),max_length=20)
    usage_count = models.PositiveIntegerField(null=True,default = 0)
    force_disable = models.BooleanField(default = False)
    start_job_id = models.CharField(max_length =100,null = True)
    end_job_id = models.CharField(max_length =100,null = True)
    @property
    def usage_exceeded(self):                    #To check if usage limit exceeded max limit
        if self.usage_count >= self.max_usage_limit:
            return True
        else:
            return False


class UserCoupon(models.Model):
    coupon = models.ForeignKey("coupons.Coupon", verbose_name="Coupon", on_delete=models.CASCADE,related_name="user_coupon")
    user = models.ForeignKey("accounts.Myuser", on_delete = models.CASCADE,related_name="user_coupon")
    usage = models.IntegerField(default = 0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['coupon', 'user'], name='unique coupon for user')
        ]
    def __str__(self):
        return self.coupon.coupon_code
    
    @property
    def is_redeemable(self):
        if self.coupon.status != 'Active':
            return False
        elif self.coupon.coupon_type == 'Normal':
            if self.usage < self.coupon.max_usage_per_user_limit and self.user.cart.total >= self.coupon.min_purchase_amount:
                return True
            else:
                return False
        else:
            if self.user.orders.filter(status='Completed').count()+1 == self.coupon.order_no and self.user.cart.total >= self.coupon.min_purchase_amount:
                return True
            else:
                return False
    @property
    def redemptions_left(self):
        if self.coupon.coupon_type == 'Order Specific':
            if self.user.orders.filter(status='Completed').count()+1 <= self.coupon.order_no:
                return 1
            else:
                return 0
            
        else:
            return self.coupon.max_usage_per_user_limit - self.usage

# redeemable == true ----->>>> add coupon to cart,when we add a new item or remove item,check is redeemable and remove coupon from cart if redeemable is false, and also when user logouts



@receiver(pre_save, sender=Coupon)
def pre_save_receiver(sender,instance, **kwargs):
    if instance.id:
        old_coupon = Coupon.objects.get(id = instance.id)
        if instance.force_disable == True:
            instance.status = 'Expired'
        elif instance.coupon_type == 'Specific Order':

            instance.status = 'Active'
            if instance.start_job_id is not None:
                scheduler.cancel(instance.start_job_id)
            if instance.end_job_id is not None:
                scheduler.cancel(instance.end_job_id)
        elif instance.coupon_type == 'Normal' and instance.usage_exceeded == True:

            instance.status = 'Expired'
            if instance.end_job_id is not None:
                scheduler.cancel(instance.end_job_id)
        elif instance.valid_from is not None and instance.valid_from < timezone.now() and instance.valid_till > timezone.now():
            instance.status = 'Active'
            if old_coupon.valid_till is None:
                if instance.valid_till != old_coupon.valid_till:
                    job = scheduler.enqueue_at(instance.valid_from,coupons.tasks.end_coupon,instance.id)
                    instance.end_job_id = job.id
            else:
                if instance.valid_till != old_coupon.valid_till:
                    scheduler.cancel(old_coupon.end_job_id)
                    job = scheduler.enqueue_at(instance.valid_from,coupons.tasks.end_coupon,instance.id)
                    instance.end_job_id = job.id
        elif instance.valid_from is not None and instance.valid_from > timezone.now():
            instance.status = 'Upcoming'
            if old_coupon.valid_from is None:
                if instance.valid_from != old_coupon.valid_from:
                    job = scheduler.enqueue_at(instance.valid_from,coupons.tasks.start_coupon,instance.id)
                    instance.start_job_id = job.id
            else:
                if instance.valid_from != old_coupon.valid_from:
                    scheduler.cancel(old_coupon.start_job_id)
                    job = scheduler.enqueue_at(instance.valid_from,coupons.tasks.start_coupon,instance.id)
                    instance.start_job_id = job.id
            
    else:
        if instance.force_disable == True:
            instance.status = "Expired"
        if instance.coupon_type == 'Specific Order':
            instance.status = 'Active'
        elif instance.valid_till is not None and instance.valid_till < timezone.now():
            instance.status = "Expired"
        elif instance.valid_from is not None and instance.valid_from > timezone.now():
            instance.status = "Upcoming"
            #------schedule tsk in post save---------
        else:
            instance.status = "Active"
    
@receiver(post_save, sender=Coupon)
def post_save_receiver(sender,instance, **kwargs):
    if instance.start_job_id is None and instance.status == "Upcoming":
        job = scheduler.enqueue_at(instance.valid_from,coupons.tasks.start_coupon,instance.id)
        instance.start_job_id = job.id
        instance.save()
    if instance.end_job_id is None and instance.valid_till is not None and instance.status == "Active":
        job = scheduler.enqueue_at(instance.valid_till,coupons.tasks.end_coupon,instance.id)
        instance.end_job_id = job.id
        instance.save()