from django.urls import path
from cart.views import (
cart_view,
add_cart_item,
cart_counter,
quantity_update,
view_redeemable_coupons
)

urlpatterns = [
    path('cart/',cart_view,name='cart'),
    path('cart/update/',add_cart_item,name='update_cart'),
    path('cart/counter/',cart_counter,name='cart-counter'),
    path('cart/updatequantity/',quantity_update, name='quantity-update'),
    path('cart/view_redeemable_coupons/',view_redeemable_coupons,name='usercoupons'),
    
]
