from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
import datetime
from datetime import timedelta
from django.views.decorators.cache import never_cache
import pytz
from offerss.forms import CategoryOfferCreateForm, CategoryOfferEditForm, ProductOfferCreateForm, ProductOfferEditForm
#-----------------
from redis import Redis
from rq import Queue
from rq_scheduler import Scheduler

from offerss.models import CategoryOffer, ProductOffer
from products.models import Category, Game
import offerss.tasks
# Create your views here.

scheduler = Scheduler(connection=Redis(host="redis_service"))


def offer_list_view(request):
    ongoing_category_offers_count = CategoryOffer.objects.filter(status = "Ongoing").count()
    upcoming_category_offers_count = CategoryOffer.objects.filter(status = "Upcoming").count()
    expired_category_offers_count = CategoryOffer.objects.filter(status = "Expired").count()
    ongoing_product_offers_count = ProductOffer.objects.filter(status = "Ongoing").count()
    upcoming_product_offers_count = ProductOffer.objects.filter(status = "Upcoming").count()
    expired_product_offers_count = ProductOffer.objects.filter(status = "Expired").count()
    category_offers = CategoryOffer.objects.all()
    product_offers = ProductOffer.objects.all()
    context={
        'ongoing_category_offers_count': ongoing_category_offers_count,
        'upcoming_category_offers_count': upcoming_category_offers_count,
        'expired_category_offers_count': expired_category_offers_count,
        'ongoing_product_offers_count': ongoing_product_offers_count,
        'upcoming_product_offers_count': upcoming_product_offers_count,
        'expired_product_offers_count': expired_product_offers_count,
        'category_offers': category_offers,
        'product_offers': product_offers,
    }
    return render(request,'offers/offerlist.html',context)

@never_cache
def category_offer_delete_view(request,id):
    offer = CategoryOffer.objects.get(id=id)
    if offer.status == "Ongoing":
        messages.error(request,"You cannot delete an going offer, you can stop the offer by disabling it")
       
    elif offer.status == 'Expired':
        messages.error(request,'You cannot delete an expired offer')
    else:
        try:
            scheduler.cancel(offer.start_job_id)
        except:
            pass
        offer.delete()
        messages.success(request,f"Upcoming offer {offer.name} deleted successfully")
    return redirect('offerlist')

def category_offer_disable_view(request,id):
    offer = CategoryOffer.objects.get(id=id)
    if offer.status =='Ongoing':
        offer.force_disable = True
        offer.valid_till = timezone.now()
        offer.save()
        scheduler.cancel(offer.end_job_id)
        offerss.tasks.end_category_offer(offer.id)
        messages.success(f"Category offer {offer.name} stopped successfully")
    else:
        messages.error("Only ongoing offers can be stopped")
    return redirect('offerlist')


@never_cache
def category_offer_add_view(request):
    form = CategoryOfferCreateForm()
    today = timezone.now()+timedelta(minutes=2)
    today = today.strftime('%Y-%m-%d %H:%M')
    # scheduler.enqueue_at(time,printsname)
    if request.method == 'POST':
        form = CategoryOfferCreateForm(request.POST)
        if form.is_valid():
            name = request.POST.get('name')
            form.save()
            messages.success(request,f"New category offer {name} added successfully")
            return redirect('offerlist')
    context = {
        'form' : form,
        'today' : today,
    }
    return render(request,'offers/addcategoryoffer.html',context)

def change_valid_till_field(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        valid_from = request.GET.get('date')
        converted_valid_from = datetime.datetime.strptime(valid_from,"%Y-%m-%d %H:%M").replace(tzinfo=pytz.UTC)
        category_id = request.GET.get('category_id')
        category = Category.objects.get(id= category_id)
        
        if category.category_offer.filter(status = 'Upcoming').exists():
            upcoming_offers = category.category_offer.filter(status = 'Upcoming').order_by('valid_from')
            for offer in upcoming_offers:
                if converted_valid_from < offer.valid_from:
                    end_date = offer.valid_from-timedelta(minutes=10)            # ends 10 mins before the next upcoming offer
                    break
                else:
                    end_date = datetime.datetime(year=2100,month=12,day=31,hour=23,minute=59)
        else:
            end_date = datetime.datetime(year=2100,month=12,day=31,hour=23,minute=59)
        
        converted_valid_from = converted_valid_from+timedelta(minutes=10)   #-----------------valid till will be 10 mins more than valid from
        start_date = converted_valid_from.strftime('%Y-%m-%d %H:%M')
        end_date = end_date.strftime('%Y-%m-%d %H:%M')
        
        response ={'start_date':start_date,'end_date':end_date}
    return JsonResponse(response)

def change_category_option(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        list = []
        id = request.GET.get('category_id')
        try:
            offer_id = request.GET.get('offer_edit_id')
            edit_offer = CategoryOffer.objects.get(id = offer_id)
        except:
            pass
        category = Category.objects.get(id = id)
        if category.category_offer.filter(status="Ongoing").exists():
            offer = category.category_offer.get(status="Ongoing")
            try:
                if edit_offer == offer:
                    start_date = timezone.now()+timedelta(minutes=2)
                    start_date = start_date.strftime('%Y-%m-%d %H:%M')
            except:
                start_date = offer.valid_till+timedelta(minutes=2)
                start_date = start_date.strftime('%Y-%m-%d %H:%M')
        else:
            start_date = timezone.now()+timedelta(minutes=2)
            start_date = start_date.strftime('%Y-%m-%d %H:%M')
        if category.category_offer.filter(status='Upcoming').exists():
            for offer in category.category_offer.filter(status='Upcoming'):
                try:
                    if offer != edit_offer:
                        valid_from = offer.valid_from
                        valid_till = offer.valid_till

                        list.append({'from':offer.valid_from.strftime('%Y-%m-%d'),'to':offer.valid_till.strftime('%Y-%m-%d')})
                except:
                        valid_from = offer.valid_from
                        valid_till = offer.valid_till
                        difference = (valid_till - valid_from).days
                        list.append({'from':offer.valid_from.strftime('%Y-%m-%d'),'to':offer.valid_till.strftime('%Y-%m-%d')})
        # newlist = sorted(list, key=lambda d: d['from'],reverse=True)
        # print(newlist)
        response = {'disable_list':list,'start_date':start_date}
        return JsonResponse(response)

@never_cache
def edit_category_offer(request,id):
    offer = CategoryOffer.objects.get(id=id)
    form = CategoryOfferEditForm(id,instance = offer)
    if request.method == 'POST':
        form = CategoryOfferEditForm(id,request.POST,instance = offer)
        if form.is_valid():
            form.save()
    offer_edit_id = offer.id

    category = offer.category
    list = []

    #-----------to create start date for valid from
    if category.category_offer.filter(status = 'Ongoing').exists():
        ongoing_offer = category.category_offer.get(status = 'Ongoing')
        start_date = ongoing_offer.valid_till+timedelta(minutes=2)
        
    else:
        start_date = timezone.now()+timedelta(minutes=2)
    
    #----------to create disabled dates list
    if category.category_offer.filter(status ='Upcoming').exists():
        for upcoming_offer in category.category_offer.filter(status ='Upcoming'):
            if upcoming_offer != offer:
               list.append({'from':upcoming_offer.valid_from.strftime('%Y-%m-%d'),'to':upcoming_offer.valid_till.strftime('%Y-%m-%d')})

        for upcoming_offer in category.category_offer.filter(status ='Upcoming').order_by('valid_from'):
            if upcoming_offer != offer:
                if offer.valid_from < upcoming_offer.valid_from:
                    max_date_valid_till = upcoming_offer.valid_from-timedelta(minutes=10)
                    break
                
    
    else:
        max_date_valid_till = datetime.datetime(year=2100,month=12,day=31,hour=23,minute=59)

    start_date = start_date.strftime('%Y-%m-%d %H:%M')

    start_date_valid_till = offer.valid_from+timedelta(minutes=5)
    start_date_valid_till = start_date_valid_till.strftime('%Y-%m-%d %H:%M')
    try:
        max_date_valid_till = max_date_valid_till.strftime('%Y-%m-%d %H:%M')
    except: 
        max_date_valid_till = datetime.datetime(year=2100,month=12,day=31,hour=23,minute=59)
        max_date_valid_till = max_date_valid_till.strftime('%Y-%m-%d %H:%M')

    context = {
        'form' : form,
        'offer_edit_id' : offer_edit_id,
        'start_date' : start_date,
        'disable_list' :  list,
        'start_date_valid_till': start_date_valid_till,
        'max_date_valid_till' : max_date_valid_till,

    }
    return render(request,'offers/editcategoryoffer.html',context)

#-----------------------------------------------------Product Offer-----------------------------------------------------------------------

@never_cache
def product_offer_add_view(request):
    form = ProductOfferCreateForm()
    today = timezone.now()+timedelta(minutes=2)
    today = today.strftime('%Y-%m-%d %H:%M')
    if request.method == 'POST':
        form = ProductOfferCreateForm(request.POST)
        if form.is_valid():
            name = request.POST.get('name')
            form.save()
            messages.success(request,f"New product offer {name} added successfully")
            return redirect('offerlist')
    context = {
        'form' : form,
        'today' : today,
     }
    return render(request,'offers/addproductoffer.html',context)


def change_game_option(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        list = []
        id = request.GET.get('game_id')

        try:
            offer_id = request.GET.get('offer_edit_id')

            edit_offer = ProductOffer.objects.get(id = offer_id)
        except:
            pass
        game = Game.objects.get(id = id)
        if game.product_offer.filter(status="Ongoing").exists():
            offer = game.product_offer.get(status="Ongoing")
            try:
                if edit_offer == offer:
                    start_date = timezone.now()+timedelta(minutes=2)
                    start_date = start_date.strftime('%Y-%m-%d %H:%M')
            except:
                start_date = offer.valid_till+timedelta(minutes=2)
                start_date = start_date.strftime('%Y-%m-%d %H:%M')
        else:
            start_date = timezone.now()+timedelta(minutes=2)
            start_date = start_date.strftime('%Y-%m-%d %H:%M')
        if game.product_offer.filter(status='Upcoming').exists():
            for offer in game.product_offer.filter(status='Upcoming'):
                try:
                    if offer != edit_offer:
                        list.append({'from':offer.valid_from.strftime('%Y-%m-%d'),'to':offer.valid_till.strftime('%Y-%m-%d')})
                except:
                        list.append({'from':offer.valid_from.strftime('%Y-%m-%d'),'to':offer.valid_till.strftime('%Y-%m-%d')})
        # newlist = sorted(list, key=lambda d: d['from'],reverse=True)
        # print(newlist)
        response = {'disable_list':list,'start_date':start_date}
        return JsonResponse(response)

def change_valid_till_field_game(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        valid_from = request.GET.get('date')
        converted_valid_from = datetime.datetime.strptime(valid_from,"%Y-%m-%d %H:%M").replace(tzinfo=pytz.UTC)

        game_id = request.GET.get('game_id')
        game = Game.objects.get(id= game_id)
        

        if game.product_offer.filter(status = 'Upcoming').exists():
            upcoming_offers = game.product_offer.filter(status = 'Upcoming').order_by('valid_from')
            for offer in upcoming_offers:
                if converted_valid_from < offer.valid_from:
                    end_date = offer.valid_from-timedelta(minutes=10)            # ends 10 mins before the next upcoming offer
                    break
                else:
                    end_date = datetime.datetime(year=2100,month=12,day=31,hour=23,minute=59)
        else:
            end_date = datetime.datetime(year=2100,month=12,day=31,hour=23,minute=59)
        
        converted_valid_from = converted_valid_from+timedelta(minutes=10)   #-----------------valid till will be 10 mins more than valid from
        start_date = converted_valid_from.strftime('%Y-%m-%d %H:%M')
        end_date = end_date.strftime('%Y-%m-%d %H:%M')
        
        response ={'start_date':start_date,'end_date':end_date}
    return JsonResponse(response)

@never_cache
def edit_product_offer(request,id):
    offer = ProductOffer.objects.get(id=id)
    form = ProductOfferEditForm(id,instance = offer)
    if request.method == 'POST':
        form = ProductOfferEditForm(id,request.POST,instance = offer)
        if form.is_valid():
            form.save()
    offer_edit_id = offer.id

    game = offer.game
    list = []

    #-----------to create start date for valid from
    if game.product_offer.filter(status = 'Ongoing').exists():
        ongoing_offer = game.product_offer.get(status = 'Ongoing')
        start_date = ongoing_offer.valid_till+timedelta(minutes=5)
        
    else:
        start_date = timezone.now()+timedelta(minutes=5)
    
    #----------to create disabled dates list
    if game.product_offer.filter(status ='Upcoming').exists():
        for upcoming_offer in game.product_offer.filter(status ='Upcoming'):
            if upcoming_offer != offer:
               list.append({'from':upcoming_offer.valid_from.strftime('%Y-%m-%d'),'to':upcoming_offer.valid_till.strftime('%Y-%m-%d')})

        for upcoming_offer in game.product_offer.filter(status ='Upcoming').order_by('valid_from'):
            if upcoming_offer != offer:
                if offer.valid_from < upcoming_offer.valid_from:
                    max_date_valid_till = upcoming_offer.valid_from-timedelta(minutes=10)
                    break
                else:
                    max_date_valid_till = datetime.datetime(year=2100,month=12,day=31,hour=23,minute=59)
    
    else:
        max_date_valid_till = datetime.datetime(year=2100,month=12,day=31,hour=23,minute=59)

    start_date = start_date.strftime('%Y-%m-%d %H:%M')

    start_date_valid_till = offer.valid_from+timedelta(minutes=5)
    start_date_valid_till = start_date_valid_till.strftime('%Y-%m-%d %H:%M')
    try:
        max_date_valid_till = max_date_valid_till.strftime('%Y-%m-%d %H:%M')
    except: 
        max_date_valid_till = datetime.datetime(year=2100,month=12,day=31,hour=23,minute=59)
        max_date_valid_till = max_date_valid_till.strftime('%Y-%m-%d %H:%M')

    context = {
        'form' : form,
        'offer_edit_id' : offer_edit_id,
        'start_date' : start_date,
        'disable_list' :  list,
        'start_date_valid_till': start_date_valid_till,
        'max_date_valid_till' : max_date_valid_till,

    }
    return render(request,'offers/editproductoffer.html',context)


def product_offer_delete_view(request,id):
    print('-------------sdfgdsgdgdgdfgdgdfgdfgdgdgdfggg')
    offer = ProductOffer.objects.get(id=id)
    print(f"---------{offer}")
    if offer.status == "Ongoing":
        messages.error(request,"You cannot delete an going offer, you can stop the offer by disabling it")
       
    elif offer.status == 'Expired':
        messages.error(request,'You cannot delete an expired offer')
    else:
        try:
            scheduler.cancel(offer.start_job_id)
        except:
            pass
        offer.delete()
        messages.success(request,f"Upcoming offer {offer.name} deleted successfully")
    return redirect('offerlist')

def product_offer_disable_view(request,id):
    offer = CategoryOffer.objects.get(id=id)
    if offer.status =='Ongoing':
        offer.force_disable = True
        offer.valid_till = timezone.now()
        offer.save()
        scheduler.cancel(offer.end_job_id)
        offerss.tasks.end_category_offer(offer.id)
        messages.success(f"Product offer {offer.name} stopped successfully")
    else:
        messages.error("Only ongoing offers can be stopped")
    return redirect('offerlist')