from random import choices
from unicodedata import category
from django.db import models
from django.db.models.signals import post_save,post_delete,pre_delete,pre_save,m2m_changed
from django.dispatch import receiver
from django.utils import timezone
from redis import Redis
from rq_scheduler import Scheduler
import offerss.tasks
from django.core.validators import MaxValueValidator, MinValueValidator
# Create your models here.

scheduler = Scheduler(connection=Redis(host='redis_service'))




class OfferAbstractModel(models.Model):
    name = models.CharField(max_length=100,null=False,unique = True,blank = False)
    valid_from = models.DateTimeField(null=False,blank=False,)
    valid_till = models.DateTimeField(null=False,blank=False)
    discount_percentage = models.PositiveIntegerField(null=True,validators=[MaxValueValidator(60),MinValueValidator(5)])
    status = models.CharField(max_length=20,choices=(('Upcoming','Upcoming'),('Ongoing','Ongoing'),('Expired','Expired'),))
    start_job_id = models.CharField(max_length =100,null = True)
    end_job_id = models.CharField(max_length=100,null = True,)
    force_disable = models.BooleanField(null = True)
    @property
    def check_is_active(self):
        # datetime.datetime.strptime(self.valid_from, '%Y-%m-%d %I:%M')
        if self.valid_from <= timezone.now() and self.valid_till >= timezone.now():
            active = True
        else:
            active = False
        return active

    class Meta:
        abstract = True

class ProductOffer(OfferAbstractModel):
    game=models.ForeignKey("products.Game", verbose_name="Game",related_name="product_offer",on_delete=models.CASCADE,null=True)

    def get_absolute_url(self):
        return self.id
    
    def __str__(self):
        return self.name


class CategoryOffer(OfferAbstractModel):
    category=models.ForeignKey("products.Category", verbose_name="Category",related_name="category_offer",on_delete=models.CASCADE,null=True)
    

    def get_absolute_url(self):
        return self.id
    
    def __str__(self):
        return self.name

class MainSaleOffer(OfferAbstractModel):
    type = models.CharField(choices=(("Categories","Categories"),("Games","Games")),max_length=10)
    categories = models.ManyToManyField("products.category",related_name="sale_offer",)
    games = models.ManyToManyField("products.Game",related_name="sale_offer")


#-----------------------------CategoryOffer-------SIGNALS------------------------#



@receiver(pre_save, sender=CategoryOffer)
def pre_save_receiver(sender,instance, **kwargs):
    if instance.id:
        offer = CategoryOffer.objects.get(id = instance.id)
        if instance.valid_from < timezone.now() and instance.valid_till >= timezone.now():
            instance.status = 'Ongoing'
            
            if instance.valid_till != offer.valid_till:
                scheduler.cancel(offer.end_job_id)
                job = scheduler.enqueue_at(instance.valid_till,offerss.tasks.end_category_offer,instance.id)
                instance.end_job_id = job.id
        
        elif instance.valid_from > timezone.now() and instance.valid_till >= timezone.now():
            instance.status = 'Upcoming'
            
            if instance.valid_from != offer.valid_from:
                scheduler.cancel(offer.start_job_id)
                job = scheduler.enqueue_at(instance.valid_from,offerss.tasks.start_category_offer,instance.id)
                instance.start_job_id = job.id

            if instance.category != offer.category:
                scheduler.cancel(offer.start_job_id)
                job = scheduler.enqueue_at(instance.valid_from,offerss.tasks.start_category_offer,instance.id)
                instance.start_job_id = job.id
            
        elif instance.valid_till < timezone.now():
            instance.status = 'Expired'

    else:
        if instance.valid_from < timezone.now() and instance.valid_till >= timezone.now():
            instance.status = 'Ongoing'

        elif instance.valid_from > timezone.now() and instance.valid_till >= timezone.now():
            instance.status = 'Upcoming'
        elif instance.valid_till < timezone.now():
            instance.status = 'Expired'
        
    
    


@receiver(post_save, sender=CategoryOffer)
def post_save_receiver(sender,instance, **kwargs):
    if instance.status == 'Ongoing' and instance.end_job_id is None:
        offerss.tasks.start_category_offer(instance.id) #........ starting offer without scheduling it
       
    elif instance.status == 'Upcoming' and instance.start_job_id is None:
        job = scheduler.enqueue_at(instance.valid_from,offerss.tasks.start_category_offer,instance.id) #..........scheduled at upcoming date
        instance.start_job_id = job.id
        instance.save()
        
    


@receiver(pre_delete, sender=CategoryOffer)
def pre_delete_receiver(sender,instance, **kwargs):
    category = instance.category

    if instance.status == 'Upcoming':
        pass
    elif instance.status == 'Ongoing':
        raise Exception("Cannot delete ongoing offer")
    else:
        raise Exception("Cannot delete expired offer")


#-----------------------------------------------------------------------------------------#

@receiver(pre_save, sender=ProductOffer)
def productOffer_pre_save_receiver(sender,instance, **kwargs):
    if instance.id:

        offer = ProductOffer.objects.get(id = instance.id)
        if instance.valid_from < timezone.now() and instance.valid_till >= timezone.now():
            instance.status = 'Ongoing'
            
            if instance.valid_till != offer.valid_till:
                scheduler.cancel(offer.end_job_id)
                job = scheduler.enqueue_at(instance.valid_till,offerss.tasks.end_product_offer,instance.id)
                instance.end_job_id = job.id
        
        elif instance.valid_from > timezone.now() and instance.valid_till >= timezone.now():
            instance.status = 'Upcoming'
            
            if instance.valid_from != offer.valid_from:
                scheduler.cancel(offer.start_job_id)
                job = scheduler.enqueue_at(instance.valid_from,offerss.tasks.start_product_offer,instance.id)
                instance.start_job_id = job.id

            if instance.game != offer.game:
                scheduler.cancel(offer.start_job_id)
                job = scheduler.enqueue_at(instance.valid_from,offerss.tasks.start_product_offer,instance.id)
                instance.start_job_id = job.id
            
        elif instance.valid_till < timezone.now():
            instance.status = 'Expired'
    else:
        if instance.valid_from < timezone.now() and instance.valid_till >= timezone.now():
            instance.status = 'Ongoing'

        elif instance.valid_from > timezone.now() and instance.valid_till >= timezone.now():
            instance.status = 'Upcoming'
        elif instance.valid_till < timezone.now():
            instance.status = 'Expired'

@receiver(post_save, sender=ProductOffer)
def productOffer_post_save_receiver(sender,instance, **kwargs):
    if instance.status == 'Ongoing' and instance.end_job_id is None:
        offerss.tasks.start_product_offer(instance.id)  #.....................starting offer without scheduling it
        
    elif instance.status == 'Upcoming' and instance.start_job_id is None:
        job = scheduler.enqueue_at(instance.valid_from,offerss.tasks.start_product_offer,instance.id)
        instance.start_job_id = job.id
        instance.save()
    else:
        pass
        
    


        

    
@receiver(post_delete, sender=ProductOffer)
def productOffer_pre_delete_receiver(sender,instance, **kwargs):
    if instance.status == "Upcoming":
        try:
            scheduler.cancel(instance.start_job_id)
        except:
            pass
    elif instance.status == 'Ongoing':
        raise Exception("Cannot delete ongoing offer")
    else:
        raise Exception("Cannot delete expired offer")

#-----------------------------------------------------main sale signals--------------------------------------------------------

# @receiver(m2m_changed, sender=MainSaleOffer.categories.through)
# def testingmm(sender,instance, action, pk_set, **kwargs):
#     print("----------------------------Entering m2m change singnal---------------------------")
#     if action == 'post_remove':
#         print(pk_set)
#     if action == 'post_add':
#         print(pk_set)


