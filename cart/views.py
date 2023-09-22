import json
from operator import ne
from pydoc import resolve
from urllib import response
from django.shortcuts import render
from cart.models import Cart,cartItem
from accounts.models import MyUser
from coupons.models import Coupon, UserCoupon
from products.models import Game
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from django.views.decorators.cache import never_cache
from django.views.decorators.clickjacking import xframe_options_exempt

# Create your views here.
@never_cache
def cart_view(request):
    try:
        cart = Cart.objects.get(user_id=request.user.id)
        
    except:
        session=Session.objects.get(session_key=request.session.session_key)
        cart = Cart.objects.get(session=session)
   
    cartitems = cart.items.all()
    redeemable_coupons = []
    if request.user.is_authenticated:
        active_coupons = Coupon.objects.filter(status = 'Active')
        for coupon in active_coupons:
            if coupon.custom_user is not None:
                if coupon.custom_user == request.user:
                    UserCoupon.objects.get_or_create(user = request.user, coupon = coupon)
                else:
                    pass
            else:
                UserCoupon.objects.get_or_create(user = request.user, coupon = coupon)
        user_coupons = UserCoupon.objects.filter(user=request.user)
        redeemable_coupons = []
        
        for coupon in user_coupons:
            if coupon.is_redeemable == True:
                redeemable_coupons.append(coupon)
    else:
        pass
        
    context={
        'cart':cart,
        'cartitems':cartitems,
        'redeemable_coupons' : redeemable_coupons,
        # 'session_key':session_key,
    }
    return render(request,'cart/cart.html',context)

@xframe_options_exempt
def view_redeemable_coupons(request):
    if request.user.is_authenticated:
        user_coupons = UserCoupon.objects.filter(user=request.user)
        redeemable_coupons = []
        non_redeemable_coupons = []
        for coupon in user_coupons:
            if coupon.is_redeemable == True:
                redeemable_coupons.append(coupon)

            else:
                if coupon.coupon.status != 'Expired':
                    non_redeemable_coupons.append(coupon)
        order_no=request.user.orders.filter(status ='Completed').count()+1
        context = {
            'order_no':order_no,
            'redeemable_coupons': redeemable_coupons,
            'non_redeemable_coupons': non_redeemable_coupons,
        }
        return render(request,'coupons/usercoupons.html',context)

@never_cache       
def add_cart_item(request):
    data = json.loads(request.body)
    gameId = data['gameId']
    action = data['action']
    if request.user.is_authenticated:
        user_cart = request.user.cart
    else:
        session=Session.objects.get(session_key=request.session.session_key)

        user_cart = Cart.objects.get(session=session)

    game=Game.objects.get(id=gameId)
    itemcount=cartItem.objects.filter(game=game,cart=user_cart).count()

    if action == 'add':
        if itemcount<=0:
            item = cartItem.objects.create(game=game,cart=user_cart)

            return JsonResponse(data={'add':'Added to cart'})
        else:
            item = cartItem.objects.get(game=game,cart=user_cart)
            if item.quantity + 1 <= game.max_quantity:
                item.quantity = item.quantity+1
                item.save()
                return JsonResponse(data={'message':'Quantity increased by 1'})
            else:
                return JsonResponse(data={'message_error':'Limit per purchase reached'})

    elif action =='remove':
        item = cartItem.objects.get(game=game, cart = user_cart)
        item.delete()
        if request.user.is_authenticated:
            if user_cart.coupon is not None:
                if not user_cart.coupon.is_redeemable:
                    user_cart.coupon = None
                    user_cart.save()
                    coupon_message = "Coupon removed from cart!!!!!!!"
        try:
            return JsonResponse(data={'remove':'Removed from cart','coupon_messsage':coupon_message})
        except:
            return JsonResponse(data={'remove':'Item removed from cart'})

@never_cache
def cart_counter(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            cart = request.user.cart
        except:
            session=Session.objects.get(session_key=request.session.session_key)
            cart = Cart.objects.get(session=session)
            
        response={
            'cart_count':cart.count,
            'cart_total' : cart.total,
            'cart_id':cart.id,
        }
        return JsonResponse(response)
    else:
        pass

def quantity_update(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        itemId = (request.GET.get('itemId'))
        action = (request.GET.get('action'))
        print('------------------------------------------')
        item = cartItem.objects.get(id=itemId)
        print(f'------------------{item}')
        print('@@@@@@@@@@@@@@@')
        print(request.user)
        if request.user.is_authenticated:
            user_cart = request.user.cart
            print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
        else:
            session=Session.objects.get(session_key=request.session.session_key)
            user_cart = Cart.objects.get(session=session)
            print('--------------------aaaaaaaaaaaaaaa')
            print(user_cart)
        if action == 'add':
            check = item.quantity+1
            if check <= item.game.max_quantity:
                item.quantity += 1
                item.save()
                response={
                    'cart_total':user_cart.total,
                    'item_quantity':item.quantity,
                    'max_quantity':item.game.max_quantity,
                }
                return JsonResponse(response)
            else:
                response={
                        'max_quantity':item.game.max_quantity,
                        'item_quantity':item.quantity,
                        'message':'Limit per purchase reached',
                    }
                return JsonResponse(response)

        elif action == 'remove':
            check = item.quantity-1
            if check >= 1:
                item.quantity -= 1
                item.save()
                if request.user.is_authenticated:
                    if user_cart.coupon is not None:
                        if not user_cart.coupon.is_redeemable:
                            user_cart.coupon = None
                            user_cart.save()
                            removed = True
                        else:
                            removed = False
                    else:
                        removed = False
                removed = False
                response={
                    'removed' : removed,
                    'max_quantity':item.game.max_quantity,
                    'cart_total':user_cart.total,
                    'item_quantity':item.quantity,
                }
                return JsonResponse(response)
            else:
                response={
                    'max_quantity':item.game.max_quantity,
                    'message':'Cannot decrease quantity beyond 1',
                }
                return JsonResponse(response)
