
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MonkeyGameStore.settings')
django.setup()
from rq_scheduler import Scheduler
from redis import Redis
import offerss.tasks

import offerss.models

scheduler = Scheduler(connection=Redis(host="redis_service"))

def printsname():
    print('------------------------------------------!!!!!!!!!!!!!!!!!!!!!!!!!!')



def start_category_offer(id):
    offer = offerss.models.CategoryOffer.objects.get(id=id)
    offer.status = 'Ongoing'
    job = scheduler.enqueue_at(offer.valid_till,offerss.tasks.end_category_offer,offer.id)
    offer.end_job_id = job.id
    offer.save()
    offer.category.discount_status = True
    offer.category.save()
    games = offer.category.games.all()
    for game in games:
        if game.discount_status != 'Product Discount':
            game.discount_status = 'Category Discount'
            game.save()
            game.discount

def end_category_offer(id):
    offer = offerss.models.CategoryOffer.objects.get(id=id)
    offer.status = 'Expired'
    offer.save()
    offer.category.discount_status = False
    offer.category.save()
    games = offer.category.games.all()
    for game in games:
        if game.discount_status != 'Product Discount':
            for category in game.categories.all():
                if category.category_offer.filter(status="Ongoing").exists():
                    game.discount_status = 'Category Discount'
                    game.save()
                    game.discount
                else:
                    game.discount_status = 'None'
                    game.discounted_price = None
                    game.discount_name = None
                    game.discount_percentage = None
                    game.save()
                    
            
                    

def start_product_offer(id):
    offer = offerss.models.ProductOffer.objects.get(id=id)
    offer.status = "Ongoing"
    job = scheduler.enqueue_at(offer.valid_till,offerss.tasks.end_product_offer,offer.id)
    offer.end_job_id = job.id
    offer.save()
    offer.game.discount_status = "Product Discount"
    offer.game.discounted_price = offer.game.base_price - round(offer.game.base_price*(offer.discount_percentage/100),2)
    offer.game.discount_name = offer.name
    offer.game.discount_percentage = offer.discount_percentage
    offer.game.save()


def end_product_offer(id):
    offer = offerss.models.ProductOffer.objects.get(id=id)
    offer.status = "Expired"
    offer.save()
    game = offer.game
    for category in game.categories.all():
        if category.category_offer.filter(status = 'Ongoing').exists():
            game.discount_status = "Category Discount"
            game.save()
            game.discount
            break
        else:
            game.discount_status = "None"
            game.discounted_price = None
            game.discount_name = None
            game.discount_percentage = None
    game.save()