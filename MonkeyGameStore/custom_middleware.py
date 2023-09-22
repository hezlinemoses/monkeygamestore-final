from datetime import timedelta
from email.policy import strict
from django.shortcuts import redirect
from django.urls import reverse

from orders.models import BillingAddress, Order


class CustomMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        try:
            previous_link=request.META['HTTP_REFERER']
            order_id = request.session['order_id']
            
            if previous_link == request.build_absolute_uri(reverse('payment')):
                if request.path != (reverse('razorpaycomplete')) and request.path != (reverse('paypalcomplete')) and request.path != (reverse('walletcomplete')) and request.path != (reverse('orderdetail',order_id)):
                    
                
                    order_id = request.session['order_id']
                    try:
                        order = Order.objects.get(id=order_id,status="Payment Pending")
                        billing_address = BillingAddress.objects.get(id=order.billing_address.id)
                        billing_address.delete()
                        del request.session['order_id']
                    except:
                        pass
                else:
                    pass
                                                                                       
        except:
            pass
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

	# Code to be executed for each response after the view is called
        # 
        greet = 'Hello from cookie'
        response.set_cookie('test',greet,max_age=timedelta(days=1),samesite='strict',secure=True)
        if not request.user.is_authenticated:
            session = request.session.session_key
            response.set_cookie('session_transfer',session,max_age=timedelta(days=1),samesite='strict',secure=True)
        print("custom middleware after response or previous middleware")
        
        return response