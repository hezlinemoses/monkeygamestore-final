from django.http import JsonResponse
from django.shortcuts import redirect, render
import pytz
from django.contrib import messages
from coupons.models import Coupon, UserCoupon
from .forms import CouponCreateForm, CouponEditForm
from django.utils import timezone
from datetime import datetime,timedelta
from redis import Redis
from rq_scheduler import Scheduler
# Create your views here.


scheduler = Scheduler(connection=Redis(host="redis_service"))

def add_coupon_view(request):
    form = CouponCreateForm()
    today = timezone.now()
    today = today.strftime('%Y-%m-%d %H:%M')
    if request.method == 'POST':
        form = CouponCreateForm(request.POST)
        if form.is_valid():
            if form.cleaned_data.get('coupon_type') == 'Specific Order':
                coupon:Coupon = form.save(commit=False)
                coupon.max_usage_per_user_limit = 1
                coupon.save()
            else:
                form.save()
            messages.success(request,"Coupon added succesfully")
            return redirect('admin_couponlist')
    context ={
        'form': form,
        'today': today,

    }
    return render(request,'coupons/addcoupon.html',context)

def check_order(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        order_no = request.GET.get('order_no')
        if Coupon.objects.filter(status='Active',order_no=order_no).exists():
            error_message = 'An active coupon exists for this order'
        response = {
            'error_message':error_message,
        }
        return JsonResponse(response)
def edit_coupon_view(request,id):
    coupon = Coupon.objects.get(id=id)
    form =CouponEditForm(coupon,instance=coupon)
    today = timezone.now()
    today = today.strftime('%Y-%m-%d %H:%M')
    if request.method == 'POST':
        form =CouponEditForm(coupon,request.POST,instance=coupon)
        if form.is_valid():
            form.save()
            messages.success(request,"Coupon updated succesfully")
            return redirect('admin_couponlist')
        else:
            pass
    if coupon.valid_from is not None:
        if coupon.status == 'Upcoming':
            valid_till = coupon.valid_from + timedelta(minutes=10)
        else:
            valid_till = timezone.now()
    else:
        valid_till = timezone.now()

    valid_till = valid_till.strftime('%Y-%m-%d %H:%M')

    context = {
        'valid_till':valid_till,
        'edit_coupon':coupon,
        'today':today,
        'form': form,
    }

    return render(request,'coupons/editcoupon.html',context)

def coupon_list_view(request):
    coupons = Coupon.objects.all()
    context = {
        'coupons': coupons,
    }
    return render(request,'coupons/admin_couponlist.html',context)

def change_valid_till_coupon(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        date_str = request.GET.get('date')
        date = datetime.strptime(date_str,"%Y-%m-%d %H:%M").replace(tzinfo=pytz.UTC)
        valid_till = date + timedelta(minutes=10)
        valid_till_str = valid_till.strftime('%Y-%m-%d %H:%M')
        message = 'HELLO FROM SERVER'
        response ={
            'message': message,
            'start_date': valid_till_str,
        }
        return JsonResponse(response)
        
def disable_coupon_view(request,id):
    coupon = Coupon.objects.get(id = id)
    if coupon.status == 'Active':
        coupon.force_disable = True
        if coupon.end_job_id is not None:
            scheduler.cancel(coupon.end_job_id)
        coupon.save()
        messages.success(request,'Coupon disabled successfully')
        return redirect('admin_couponlist')
    else:
        messages.error(request,'Can only disable active coupons')
        return redirect('admin_couponlist')


def delete_coupon_view(request,id):
    coupon = Coupon.objects.get(id = id)
    if coupon.status == 'Upcoming':
        try:
            scheduler.cancel(coupon.start_job_id)
        except:
            pass
        coupon.delete()
        messages.success(request,'Coupon deleted successfully')
        return redirect('admin_couponlist')
    else:
        messages.error(request,'Can only delete upcoming coupons')
        return redirect('admin_couponlist')


def add_coupon_to_cart(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        coupon_code = request.GET.get('coupon_code')

        if Coupon.objects.filter(coupon_code__exact=coupon_code).exists():
            coupon = Coupon.objects.get(coupon_code=coupon_code)
            try:
                cart_coupon = UserCoupon.objects.get(coupon =coupon,user = request.user)
            except:
                message = "Coupon does't exist"
                response = {
                'error_message': message,
                }
                return JsonResponse(response)

            if cart_coupon.is_redeemable:
                request.user.cart.coupon = cart_coupon
                request.user.cart.save()
                message = "Coupon applied to cart"
                response = {
                    'message': message,
                }
            else:
                message = "Coupon is not redeemable"
                response = {
                    'error_message': message,
                }
        else:
            message = "Coupon does't exist"
            response = {
                'error_message': message,
            }

        
        return JsonResponse(response)

def remove_coupon_from_cart(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.user.is_authenticated:
            if request.user.cart.coupon is not None:
                request.user.cart.coupon = None
                request.user.cart.save()
                response ={
                    'message':"Coupon removed from cart!!!!!!"
                }
                return JsonResponse(response)

def check_user_coupon_in_cart(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.user.is_authenticated:
            if request.user.cart.coupon is not None:
                if not request.user.cart.coupon.is_redeemable:
                    request.user.cart.coupon = None
                    request.user.cart.save()
                    response = {
                        'coupon_removed': True,
                    }
                    
                else:
                    response = {
                        'coupon_removed': False,
                    }
            else:
                response = {
                        'coupon_removed': False,
                    }
            return JsonResponse(response)