
import uuid
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from requests import session

from coupons.models import Coupon
from .models import Order,OrderItem,BillingAddress
from accounts.models import MyUser, UserAddress
from .forms import AddressMethodForm, BillingAddressForm, PaymentMethod, SavedAddressSelectForm, ShippingAddressForm
from accounts.forms import UserAddressForm
from django.contrib import messages
from django.urls import reverse
import razorpay
from django.views.decorators.cache import never_cache
import random
from django.utils import timezone
from datetime import timedelta

# Create your views here.


# authorize razorpay client with API Keys.
razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

@never_cache
@login_required(login_url='login')
def checkout_view(request):
    '''
    Creates an order on post request and if forms are valid
    '''
    try:
        order_id = request.session['order_id']
        order = Order.objects.get(id=order_id,status = 'Pending Payment')
        bill_address = order.billing_address
        bill_address.delete()
        try:
            order.delete()
        except:
            pass
    except:
        pass
    cart = request.user.cart
    if cart.coupon is not None:
        if not cart.coupon.is_redeemable:
            cart.coupon = None
            cart.save()
    billform = BillingAddressForm()
    # saved_address_form = SavedAddressSelectForm(request)
    address_method_form = AddressMethodForm(request)
    check_saved_address_count = request.user.address.all().count()
    if check_saved_address_count != 0:
        saved_address_form = SavedAddressSelectForm(request)
    # shipform = ShippingAddressForm()
    
    if cart.count <= 0:
        return redirect('home')
    cartitems = cart.items.all()
    if request.method == 'POST':
        
        address_method = request.POST.get('address_method')

        billform = BillingAddressForm(request.POST)

        if address_method == 'Saved Address':
            address_id =request.POST.get('saved_addresses')
            address = UserAddress.objects.get(id=address_id)
            bill_address = BillingAddress.objects.create(
                first_name=address.first_name,
                last_name=address.last_name,
                line_1=address.line_1,
                line_2=address.line_2,
                locality=address.locality,
                city=address.city,
                state=address.state,
                country = address.country,
                pincode = address.pincode,
                Landmark = address.Landmark,
                district = address.district,
                phone = address.phone,
                user = request.user,
            )
            
            

        if address_method == 'New Address':
            if billform.is_valid():
                
                save_address=billform.cleaned_data.get('save_address')
                if save_address == True:
                    saveuser=MyUser.objects.get(id=request.user.id)
                    form:UserAddress = UserAddressForm(request.POST,initial={'user_id':saveuser})
                    user_address=form.save(commit=False)
                    user_address.user =saveuser
                    user_address.save()

                bill_address : BillingAddress = billform.save(commit=False)
                bill_address.user = request.user
                bill_address.save()
        address_id = bill_address.id
        if cart.coupon is not None:
            user_coupon = cart.coupon
            order = Order.objects.create(user = request.user,applied_coupon=user_coupon,coupon_code=cart.coupon.coupon.coupon_code,coupon_discount=cart.coupon_discount,billing_address = bill_address,status = 'Pending Payment')
        else:
            order = Order.objects.create(user = request.user,billing_address = bill_address,status = 'Pending Payment')

        #----------------adding items to order----------------------#

        for item in cartitems:

            orderitem : OrderItem = OrderItem.objects.create(
                game=item.game,
                item_price=item.game.base_price,
                order = order,
                title = item.game.title,
                item_thumbnail=item.game.thumbnail,
                quantity = item.quantity,
                item_offer_discount_given = item.item_offer_discount,
                item_offer_discount_percentage = item.game.discount_percentage,
                item_offer_discount_status = item.game.discount_status,
                item_offer_discount_name = item.game.discount_name,
                )
            # item.delete()

        request.session['order_id'] = order.id
        request.session['address_id'] = address_id

        # messages.success(request,f"Your order has been placed")
        return redirect('payment',)
      
    
    if check_saved_address_count != 0:
        context={
            'saved_address_form' : saved_address_form,
            'address_method_form' : address_method_form,
            'billform' : billform,
            'cartitems' : cartitems,
            'cart' : cart,
        }
    else:
        context={
            # 'saved_address_form' : saved_address_form,
            'address_method_form' : address_method_form,
            'billform' : billform,
            'cartitems' : cartitems,
            'cart' : cart,
        }
            

   
    return render(request,'orders/checkout.html',context)

@never_cache
@login_required(login_url='login')
def payment_method_view(request):
    try:
        previous_link=request.META['HTTP_REFERER']
    except:
        return redirect('checkout')
   
    if previous_link == request.build_absolute_uri(reverse('checkout')):
        order_id = request.session['order_id']
        paymentform = PaymentMethod()
        try:
            order = Order.objects.get(id=order_id,status='Pending Payment')
        except:
            return redirect('home')
        cart = request.user.cart
        cartitems = cart.items.all()
        orderitems = order.items.all()

        for item in cartitems:
            print(item)

        #------------------------Razorpay things---------------------------------------#
        amount = int(order.total)*100

        payment = razorpay_client.order.create({'amount': amount, 'currency': 'INR', 'payment_capture':1 })



        context = {
            'orderitems':orderitems,
            'cartitems' : cartitems,
            'paymentform':paymentform,
            'order' : order,
            'cart' : cart,
            #--------Razorpay things--------#
            'payment' : payment,
        }
        return render(request,'orders/payment.html',context)
    else:
        return redirect('cart')
@never_cache
@login_required(login_url='login')
def paypal_payment_complete(request):
    try:
        order_id = request.session['order_id']
    except:
        return redirect('home')
    order = Order.objects.get(id=order_id)
    order.status = 'Completed'
    order.payment_method = "Paypal"
    if order.applied_coupon is not None:
        order.applied_coupon.usage += 1
        order.applied_coupon.save()
        order.applied_coupon.coupon.usage_count += 1
        order.applied_coupon.coupon.save()
    order.db_total = order.total
    order.save()
    for item in order.items.all():
        item.game.salecount += item.quantity
        item.game.save()
    cart = request.user.cart
    cartitems = cart.items.all()
    for item in cartitems:
        item.delete()
    cart.coupon = None
    cart.save()
    del request.session['order_id']
    coupon_given=random_coupon(request=request)
    if coupon_given:
        messages.success(request,'Order placed and coupon generated successfully')
    else:
        messages.success(request,'Order placed and successfully, coupon not generated better luck next time.')
    return redirect('orderdetail',order.id)

@never_cache
@login_required(login_url='login')
def razorpay_payment_complete(request):
    try:
        order_id = request.session['order_id']
    except:
        return redirect('home')
    order = Order.objects.get(id=order_id)
    order.status = 'Completed'
    order.payment_method = "Razorpay"
    if order.applied_coupon is not None:
        order.applied_coupon.usage += 1
        order.applied_coupon.save()
        order.applied_coupon.coupon.usage_count += 1
        order.applied_coupon.coupon.save()
    order.db_total = order.total
    order.save()

    for item in order.items.all():
        item.game.salecount += item.quantity
        item.game.save()
    cart = request.user.cart
    cartitems = cart.items.all()
    for item in cartitems:
        item.delete()
    cart.coupon = None
    cart.save()
    del request.session['order_id']
    coupon_given=random_coupon(request=request)
    if coupon_given:
        messages.success(request,'Order placed and coupon generated successfully')
    else:
        messages.success(request,'Order placed and successfully, coupon not generated better luck next time.')
    messages.success(request,'Order placed successfully')
    return redirect('orderdetail',order.id)

@never_cache
@login_required(login_url='login')
def wallet_payment_complete(request):

    try:
        order_id = request.session['order_id']
    except:
        return redirect('home')
    order = Order.objects.get(id=order_id)
    if order.total <= request.user.wallet:
        order.status = 'Completed'
        
        order.payment_method = "Wallet"
        if order.applied_coupon is not None:
            order.applied_coupon.usage += 1
            order.applied_coupon.save()
            order.applied_coupon.coupon.usage_count += 1
            order.applied_coupon.coupon.save()
        order.db_total = order.total
        order.save()
        for item in order.items.all():
            item.game.salecount += item.quantity
            item.game.save()
        cart = request.user.cart
        cartitems = cart.items.all()
        for item in cartitems:
            item.delete()
        cart.coupon = None
        cart.save()
        request.user.wallet -= order.total
        request.user.save()
        del request.session['order_id']
        random_coupon(request=request)
        response={
            'success_message':'Redirecting to success page'
        }
        return JsonResponse(response)
    else:
        response={
            'error_message':'Please use another payment method',
        }
        return JsonResponse(response)




def request_refund_view(request,id):
    order = Order.objects.get(id=id)
    if order.is_refundable:
        order.status = 'Refunded'
        for item in order.items.all():
            item.game.salecount -= item.quantity
            item.game.save()
        request.user.wallet += order.db_total
        request.user.save()
        order.save()
        messages.success(request,f"Order #{order.id} cancelled, ₹{order.db_total} added to your wallet")
        return redirect('orderhistory')



#---------------------------------------------------connect this after creating change password for user and refund process..........


def random_coupon(request):
    give_cpn = ["Coupon","No Coupon"]
    random_give_cpn = random.choices(give_cpn,weights=(70,30),k=1)
    if random_give_cpn[0] == "Coupon":
        coupon_code = str(uuid.uuid4())
        custom_user = request.user
        coupon_type = 'Normal'
        discount_typ_list = ["Percentage","Amount"]
        random_discount_list = random.choices(discount_typ_list,weights=(70,30),k=1)
        if random_discount_list[0] == 'Percentage':
            discount_type = 'Percentage'
        else:
            discount_type = 'Amount'
        min_purchase_amount = 100
        max_usage_limit = 1
        max_usage_per_user_limit = 1
        valid_till = timezone.now()+timedelta(days=7)
        if discount_type == 'Percentage':
            discount_percent_value = random.randint(2,5)*5
            max_discount_amount = 100
            Coupon.objects.create(
                coupon_code=coupon_code,
                custom_user=custom_user,
                coupon_type=coupon_type,
                discount_type=discount_type,
                min_purchase_amount=min_purchase_amount,
                max_usage_limit=max_usage_limit,
                max_usage_per_user_limit=max_usage_per_user_limit,
                valid_from = timezone.now()+timedelta(seconds=15),
                valid_till=valid_till,
                discount_percent_value=discount_percent_value,
                max_discount_amount=max_discount_amount,
                )
        else:
            discount_amount_value = random.randint(10,50)
            Coupon.objects.create(
                coupon_code=coupon_code,
                custom_user=custom_user,
                coupon_type=coupon_type,
                discount_type=discount_type,
                min_purchase_amount=min_purchase_amount,
                max_usage_limit=max_usage_limit,
                valid_from=timezone.now()+timedelta(seconds=15),
                max_usage_per_user_limit=max_usage_per_user_limit,
                valid_till=valid_till,
                discount_amount_value=discount_amount_value
            )
            return True

    else:
        return False
