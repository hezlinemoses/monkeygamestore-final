from django.urls import path

from .views import(
    checkout_view,
    payment_method_view,
    paypal_payment_complete,
    razorpay_payment_complete,
    request_refund_view,
    wallet_payment_complete,

)


urlpatterns = [
    path('checkout/',checkout_view,name='checkout'),
    path('checkout/payment/',payment_method_view,name='payment'),
    path('checkout/paypal/complete/',paypal_payment_complete,name='paypalcomplete'),
    path('checkout/razorpay/complete/',razorpay_payment_complete,name='razorpaycomplete'),
    path('accounts/orders/request_refund/<id>/',request_refund_view,name='requestrefund'),
    path('checkout/wallet/check',wallet_payment_complete,name='walletcomplete'),
]
