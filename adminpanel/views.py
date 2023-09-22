from ast import Not
from calendar import calendar, month
from calendar import day_name

import datetime
from datetime import date, timedelta,datetime
import decimal

from django.http import JsonResponse
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from accounts.models import MyUser
from adminpanel.forms import ReportFiltersForm
from coupons.models import Coupon
from orders.models import Order

from django.views.decorators.cache import never_cache
from orders.forms import OrderStatusChangeForm
from django.utils import timezone
from django.db.models import Sum

from products.models import Game



# Create your views here.

@never_cache
@user_passes_test(lambda u:u.is_superuser, login_url="admin_login")
def admin_dashboard_view(request):
    greeting = "Welcome to admin panel"
    
    completed_orders = Order.objects.filter(status='Completed').count()
    total_revenue = Order.objects.filter(status='Completed').aggregate(Sum('db_total'))['db_total__sum']
    top_game = Game.objects.all().order_by('-salecount')[0]
    orders = Order.objects.filter(status='Completed')
    tp_gm_rev=decimal.Decimal(0.00)
    for order in orders:
        for item in order.items.all():
            if item.game == top_game:
                tp_gm_rev += item.item_total
    tp_cp_disc = 0
    top_coupon = Coupon.objects.all().order_by('-usage_count')[0]
    for order in orders:
        if order.applied_coupon is not None:
            if order.applied_coupon.coupon == top_coupon:
                tp_cp_disc += order.coupon_discount
    users = MyUser.objects.filter(is_verified=True)

    highest_user_rev = decimal.Decimal(0.00)
    for user in users:
        user_revenue = user.orders.filter(status='Completed').aggregate(Sum('db_total'))['db_total__sum'] or 0.00
        if user_revenue > highest_user_rev:
            highest_user_rev = user_revenue
            top_user = user.username
    games = Game.objects.all()
    highest_game_rev = decimal.Decimal(0.00)
    for game in games:
        single_game_rev = decimal.Decimal(0.00)
        for sale in game.order_items.all():
            if sale.order.status == 'Completed':
                single_game_rev += sale.item_total
        if single_game_rev > highest_game_rev:
            highest_game_rev = single_game_rev
            highest_game_rev_obj = game
    form =ReportFiltersForm()
    
    context= {
        'highest_game_rev':highest_game_rev,
        'highest_game_rev_obj':highest_game_rev_obj,
        'top_user':top_user,
        'top_user_rev':highest_user_rev,
        'tp_cp_disc':tp_cp_disc,
        'top_coupon':top_coupon,
        'tp_gm_rev':tp_gm_rev,
        'top_game': top_game,
        'total_revenue':total_revenue,
        'completed_orders':completed_orders,
        'form' : form,
        'greeting': greeting,
    }
    return render( request,'adminpanel/admin_dashboard_content.html', context )

def revenue_weekly(request):
    weekly_revenue = []
    week_days = []
    sum=0
    for i in reversed(range(0,7)):
        daily_revenue = Order.objects.filter(status='Completed',created_at__date=date.today()-timedelta(days=i)).aggregate(Sum('db_total'))['db_total__sum'] or 0.00
        # daily_orders = Order.objects.filter(status='Completed',created_at__date=date.today()-timedelta(days=i)).count()
        sum = decimal.Decimal(decimal.Decimal(sum)+decimal.Decimal(daily_revenue))
        weekly_revenue.append(daily_revenue)
        day = date.today()-timedelta(days=i)
        dayname = day_name[day.weekday()]
        week_days.append(dayname)

    labels = week_days
    chartlabel = "Revenue"
    data = weekly_revenue
    
    return JsonResponse(data={
        'sum':sum,
        'labels': labels,
        'chartlabel': chartlabel,
        'data': data,
    })

def revenue_monthly(request):
    weekly_orders = []
    week_days = []
    sum=0.00
    for i in reversed(range(0,28,7)):
        daily_orders = Order.objects.filter(status='Completed',created_at__range=[datetime.now(tz=timezone.utc)-timedelta(days=i+7),datetime.now(tz=timezone.utc)-timedelta(days=i)]).aggregate(Sum('db_total'))['db_total__sum'] or 0.00
        sum = decimal.Decimal(decimal.Decimal(sum)+decimal.Decimal(daily_orders))
        weekly_orders.append(daily_orders)
        day = date.today()-timedelta(days=i+7),date.today()-timedelta(days=i)
        # dayname = day_name[day.weekday()]
        week_days.append(day)
  
    labels = week_days
    chartlabel = "Revenue"
    data = weekly_orders
    
    return JsonResponse(data={
        'sum':sum,
        'labels': labels,
        'chartlabel': chartlabel,
        'data': data,
    })

def order_weekly(request):
    weekly_orders = []
    week_days = []
    sum = 0
    for i in reversed(range(0,7)):
        # daily_orders = Order.objects.filter(status='Completed',created_at__date=date.today()-timedelta(days=i)).aggregate(Sum('db_total'))['db_total__sum'] or 0.00
        daily_orders = Order.objects.filter(status='Completed',created_at__date=date.today()-timedelta(days=i)).count()
        sum = sum+daily_orders
        weekly_orders.append(daily_orders)
        day = date.today()-timedelta(days=i)
        dayname = day_name[day.weekday()]
        week_days.append(dayname)

    labels = week_days
    chartlabel = "Orders"
    data = weekly_orders
    
    return JsonResponse(data={
        'sum':sum,
        'labels': labels,
        'chartlabel': chartlabel,
        'data': data,
    })
    
def order_monthly(request):
    weekly_orders = []
    week_days = []
    sum = 0
    for i in reversed(range(0,28,7)):
        daily_orders = Order.objects.filter(status='Completed',created_at__range=[datetime.now(tz=timezone.utc)-timedelta(days=i+7),datetime.now(tz=timezone.utc)-timedelta(days=i)]).count()
        weekly_orders.append(daily_orders)
        sum=sum+daily_orders
        day = date.today()-timedelta(days=i+7),date.today()-timedelta(days=i)
        # dayname = day_name[day.weekday()]
        week_days.append(day)
  
    labels = week_days
    chartlabel = "Orders"
    data = weekly_orders
    
    return JsonResponse(data={
        'sum':sum,
        'labels': labels,
        'chartlabel': chartlabel,
        'data': data,
    })

def admin_login_view(request):
    
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('admin_dashboard')
    
    else:
        if request.method == 'POST':
            email = request.POST.get('email')
            password = request.POST.get('password')

            user = authenticate(request, email = email, password = password)
            if user is not None:
                login(request,user)
                return redirect('admin_dashboard')
            
            else:
                messages.error(request, "email/password incorrect!!! ")
    context = {}
    return render(request,'adminpanel/admin_login.html', context)

def admin_logout_view(request):
    logout(request)
    return redirect('admin_login')


@never_cache
@user_passes_test(lambda u:u.is_superuser, login_url="admin_login")
def admin_user_type_view(request):
    context = {}
    return render(request,'admin_user_type.html',context)


@never_cache
@user_passes_test(lambda u:u.is_superuser, login_url="admin_login")
def admin_customer_list_view(request):                                      #block/unblock here (edit view next week)
    customers = MyUser.objects.all()
    context = {'customers':customers,}
    return render(request,'adminpanel/admin_customer_list.html',context)



@never_cache
@user_passes_test(lambda u:u.is_superuser, login_url="admin_login")
def customer_block_view(request,id):
    block_user = MyUser.objects.get(id=id)

    if block_user.is_blocked:
        block_user.is_blocked = False
        block_user.save()
        messages.error(request,f"{block_user.username} unblocked successfuly")
    else:
        block_user.is_blocked =True
        block_user.save()
        messages.success(request,f"{block_user.username} blocked successfuly")
    return redirect('customer_list')    
   






@never_cache
@user_passes_test(lambda u:u.is_superuser, login_url="admin_login")
def order_list_view(request):
    orders = Order.objects.all().order_by('-created_at')
    
    context = {
        'orders' : orders,
    }

    return render(request,'adminpanel/admin_orderlist.html',context)



@never_cache
@user_passes_test(lambda u:u.is_superuser, login_url="admin_login")
def order_detail_view(request,id):
    try:
        order = Order.objects.get(id=id)
    except:
        messages.error(request,"Order not found")
        return redirect('admin_orderlist')
    
    if request.method == 'POST':
        form = OrderStatusChangeForm(id,request.POST,instance = order,)
        if form.is_valid():
            order.save()
            return redirect('admin_orderdetail',id)
    else:
        form = OrderStatusChangeForm(id,instance = order,)
        
    
    context = {
        'form' : form,
        'order' : order,
    }
    return render(request,'adminpanel/order_detail.html', context)


