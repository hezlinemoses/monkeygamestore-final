from datetime import timedelta
from pydoc import resolve
from urllib import request, response
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import user_passes_test,login_required
from accounts.forms import SignUpForm, UserAddressForm, UserEmailchangeForm, UserPhoneChangeForm, UsernameChangeForm, UserPasswordChangeForm
from accounts.models import MyUser, UserAddress
from clientpanel import verify
from orders.models import Order
from .forms import VerifyForm,otpForm
from django.contrib.auth import login,authenticate,logout
from django.contrib import messages
from products.models import Category, Game
from cart.models import Cart, cartItem
from django.views.decorators.cache import never_cache
from django.db.models import Q
from django.contrib.sessions.models import Session
from django.views.decorators.clickjacking import xframe_options_exempt
# Create your views here.



@never_cache
def home_view(request):
    
    
    games = Game.objects.all().order_by('-uploaded_on')
    if 'gamelist' in request.COOKIES:
        gamelist=request.COOKIES['gamelist']
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.create(user_id=request.user.id)
        except:
            cart=Cart.objects.get(user_id=request.user.id)
        try:
            if gamelist:
                convertedgamelist = gamelist.split()                        #------------------converting string to list
                for game in convertedgamelist:
                    game = int(game)
                    #--------Checking if there is same item in cart----------#
                    itemcount = cartItem.objects.filter(game=Game.objects.get(id=game),cart=cart).count()
                    if itemcount <= 0 :
                        item = cartItem.objects.create(game=Game.objects.get(id=game),cart=cart)

                    else:
                        pass
        except:
            pass

        
        context={
            'cart':cart,
            'games': games,
            'usercart':cart,
        }
        response = render(request,'clientpanel/home.html',context)
        response.delete_cookie('gamelist')
        return response
    else:
        if not request.session.session_key:
            request.session.create()
            request.session.set_expiry(timedelta(days=2))
        session = Session.objects.get(session_key=request.session.session_key)
        try:
            cart = Cart.objects.get(session_id=session)
        except:
            cart = Cart.objects.create(session_id=session)
        
        
        context={
        'cart':cart,
        'session_id':session,
        'games': games,
        }
        response = render(request,'clientpanel/home.html',context)
        
        return response

@never_cache
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    else:
        
        if request.method == 'POST':
            email = request.POST.get('email')
            password = request.POST.get('password')

            user = authenticate(request, email = email, password = password)
            if user is not None:
                if 'session_transfer' in request.COOKIES:
                    session_transfer= request.COOKIES['session_transfer']
                    session = Session.objects.get(session_key=session_transfer)
                    session.delete()
                login(request,user)
                return redirect('home')
            
            else:
                messages.error(request, "email/password incorrect!!! ")
    context = {}
    response = render(request,'clientpanel/login.html', context)
    
    cart = Cart.objects.get(session=request.session.session_key)
    gamelist=""
    
    if cart:
        for item in cart.items.all():
            # gamelist.append(item.game.id)
            gamelist += f"{item.game.id} "
    
    response.set_cookie('gamelist',gamelist,max_age=timedelta(days=1),samesite='strict',secure=True)
    return response



@never_cache
def otp_login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    else:
        form = otpForm()
        if request.method =='POST':
            phone = request.POST.get('phone')
            # user_check = MyUser.objects.filter(phone__iexact=phone)
            try:
                user = MyUser.objects.get(phone__iexact=phone)
            except:
                user = None
                messages.error(request,"User with that phone number doesnt exist!!!")
            
            if user is not None:
                phone = '+91'+user.phone
                verify.send(phone)
                return redirect('otploginverify',user.id)
            
    return render(request,'clientpanel/otp_login.html',{'form':form})

@never_cache
def otp_login_verify(request,id):
    user = MyUser.objects.get(id__iexact=id)
    phone = '+91'+user.phone
    if request.method == 'POST':
        form = VerifyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data.get('code')

            if verify.check(phone, code):
                login(request,user)
                return redirect('home')
            else:
                messages.error(request,"Invalid code!!")
    else:
        form = VerifyForm()
    return render(request, 'clientpanel/verify.html', {'form': form,'phone':phone})



@never_cache
@user_passes_test(lambda u:u.is_anonymous,login_url='login')
def client_signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            phone = '+91'+form.cleaned_data.get('phone')
            try:
                verify.send(phone)
            except:
                messages.error(request,"OTP send failed, please enter a different phone number or try again later")
                return render(request,'clientpanel/client_signup.html',context)
            form.save()
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = authenticate(email=email, password=password)
            login(request, user)
            Cart.objects.get_or_create(user=request.user)
            return redirect('verification')
    else:
        form = SignUpForm()
    
    context={
        'form':form,
    }
    return render(request,'clientpanel/client_signup.html', context)

@never_cache
def send_verify_otp(request):
    if request.user.is_verified:
        return redirect('home')
    if request.method == 'POST':
        phone = '+91'+request.user.phone
        verify.send(phone)
        return redirect('verification')
    phone_no = request.user.phone
    context={
        'phone':phone
    }
    return render(request,'clientpanel/send_otp.html',context)

@never_cache
@login_required(login_url='login')
def verify_code_view(request):
    if request.user.is_verified:
        return redirect('home')
    phoneform = UserPhoneChangeForm(instance=request.user)
    if request.method == 'POST':
        form = VerifyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data.get('code')
            phone ='+91'+request.user.phone
            if verify.check(phone, code):
                request.user.is_verified = True
                request.user.is_customer = True
                request.user.save()
                Cart.objects.get_or_create(user=request.user)
                return redirect('home')
            else:
                messages.error(request,"Invalid code!!")
    else:
        form = VerifyForm()
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        phoneform = UserPhoneChangeForm(request.POST,instance=request.user)
        if phoneform.is_valid():
            phonenumber = '+91'+(request.POST.get('phone'))
            try:
                verify.send(phonenumber)
            except:
                response={
                    'error_message':"OTP send failed, please enter a different phone number or try again later",
                }
                return JsonResponse(response)
                
            phoneform.save()
            response={
                'phonenumber': phonenumber,
                'success_message': f"Please enter the OTP send to {phonenumber}"
            }
            return JsonResponse(response)
        else:
            response={
                'error_message':"Please Enter a valid phone number",
            }
            return JsonResponse(response)
    return render(request, 'clientpanel/verify.html', {'form': form,'phone':request.user.phone,'phoneform':phoneform,})

@never_cache
def logout_view(request):
    logout(request)
    return redirect('home')


@never_cache
def blocked_view(request):
    context={
        'message': 'You have been blocked'
    }
    return render(request,'clientpanel/blocked.html',context)


@never_cache
def game_detail_view(request, id):
    try:
        game = Game.objects.get(id=id)
    except:
        # messages.error(request,"Game not found")
        return redirect('home')
    descriptions = game.descriptions.all()
    slideimages = game.medias.all()
    try:
        cart = request.user.cart
    except:
        session=Session.objects.get(session_key=request.session.session_key)
        cart = Cart.objects.get(session=session)
    
    context={
        'cart': cart,
        'game' : game,
        'slideimages' : slideimages,
        'descriptions':descriptions,
    }
    return render(request,'clientpanel/gamedetail.html',context)

@never_cache
def store_view(request):
    games= Game.objects.all()
    categories = Category.objects.all()
    context={
        'games':games,
        'categories':categories,
    }
    return render(request,'clientpanel/store.html',context)



#-------------------------------------------------------------
@never_cache
@login_required(login_url='login')
def account_view(request):
    user = MyUser.objects.get(id=request.user.id)
    nameform = UsernameChangeForm(instance=user)
    emailform = UserEmailchangeForm(instance=user)
    phoneform = UserPhoneChangeForm(instance=user)
    user_orders = request.user.orders.filter(status='Completed').count()
    user_orders_refunded = request.user.orders.filter(status='Refunded').count()
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.POST.get('username'):
            nameform = UsernameChangeForm(request.POST,instance=user)
            if nameform.is_valid():
                nameform.save()
                response={'username_success': 'Username changed successfully'}
                return JsonResponse(response,status=200)
            else:
                response = {
                    'username_error': 'Username already exists',
                }
                return JsonResponse(response)
        elif request.POST.get('phone'):
            phoneform = UserPhoneChangeForm(request.POST,instance=user)
            if phoneform.is_valid():
                phoneform.save()
                response={'phone_success': 'Phone number changed successfully'}
                return JsonResponse(response,status=200)
            else:
                response = {
                    'phone_error': 'Phone already exists / Invalid phone number',
                }
                return JsonResponse(response)
        elif request.POST.get('email'):
            emailform = UserEmailchangeForm(request.POST,instance=user)
            if emailform.is_valid():
                emailform.save()
                response={'email_success': 'Email changed successfully'}
                return JsonResponse(response,status=200)
            else:
                response = {
                    "email_error": 'Email already exists',
                }
                return JsonResponse(response)
        else:
            pass
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        response={
            'username': request.user.username,
            'email': request.user.email,
            'phone': request.user.phone,
        }
        return JsonResponse(response,status=200)
    cart = request.user.cart
    context={
        'cart':cart,
        'user_orders':user_orders,
        'user_orders_refunded':user_orders_refunded,
        'nameform': nameform,
        'emailform':emailform,
        'phoneform':phoneform,
    }
    return render(request,'clientpanel/account.html',context)


@never_cache
@login_required(login_url='login')
def user_order_history(request):
    # orders = Order.objects.filter(user=request.user).filter(status='Pending Payment').order_by('-created_at')
    processingorders = Order.objects.filter(user=request.user).filter(status='Processing').order_by('-created_at')
    completedorders = Order.objects.filter(user=request.user).filter(status='Completed').order_by('-created_at')
    cancelledorders = Order.objects.filter(user=request.user).filter(status='Cancelled').order_by('-created_at')
    cart=request.user.cart

    context = {
        'cart' : cart,
        'processingorders' : processingorders,
        'completedorders' : completedorders,
        'cancelledorders' : cancelledorders,
    }

    return render(request,'clientpanel/orderhistory.html',context)



@never_cache
@login_required(login_url='login')
def order_detail_view(request,id):
    try:
        order = Order.objects.get(id=id)
    except:
        messages.error(request,"Order not found")
        return redirect('orderhistory') 
    cart = request.user.cart
    context = {
        'cart' : cart,
        'order' : order,
    }
    return render(request,'clientpanel/order_detail.html', context)

@never_cache
@login_required(login_url='login')
def order_cancel_view(request,id):
    try:
        order = Order.objects.get(id=id)
    except:
        messages.error(request,'Order not found')
        return redirect('orderhistory')
    
    order.status = 'Cancelled'
    order.save()
    return redirect('orderhistory')


@never_cache
@login_required(login_url='login')
def address_list_view(request):
    addresslist = request.user.address.all()
    # form = UserAddressForm()
    if request.method == 'POST':
        form = UserAddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            form = UserAddressForm()
            messages.success(request,f"Address added successfully")
            return redirect('addresslist')
    else:
        form = UserAddressForm()
    context = {
        'addresslist' : addresslist,
        'form' : form,
    }
    return render(request,'clientpanel/addresslist.html',context)

@xframe_options_exempt
@login_required(login_url='login')
def address_edit_view(request,id):
    address = UserAddress.objects.get(id=id)
    if request.method=='POST':
        form = UserAddressForm(request.POST,instance=address)
        if form.is_valid():
            form.save()
            messages.success(request,"Address editted successfully")
            return redirect('addressedit',id)
    else:
        form = UserAddressForm(instance=address)
    
    context ={
        'form' : form,
    }
    return render(request,'clientpanel/addressedit.html',context)

@login_required(login_url='login')
def address_delete_view(request,id):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        address = UserAddress.objects.get(id=id)
        address.delete()
        response={
            'message':'Address deleted successfully',
            'id': address.id,
        }
        return JsonResponse(response,status=200)



def forgot_password(request):
    password_form = UserPasswordChangeForm()
    return render(request,'clientpanel/forgotpassword.html',)