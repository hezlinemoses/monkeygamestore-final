from django.urls import path
from .views import(
    add_coupon_view,
    change_valid_till_coupon,
    coupon_list_view,
    disable_coupon_view,
    delete_coupon_view,
    add_coupon_to_cart,
    remove_coupon_from_cart,
    edit_coupon_view,
    coupon_list_view,
    check_user_coupon_in_cart,
    check_order,
)

urlpatterns = [
    path('admin_panel/coupons/addcoupon/',add_coupon_view,name='addcoupon'),
    path('admin_panel/coupons/editcoupon/<id>/',edit_coupon_view,name='editcoupon'),
    path('admin_panel/coupons/',coupon_list_view,name='admin_couponlist'),
    path('admin_panel/coupons/addcoupon/change_valid_till/',change_valid_till_coupon),
    path('admin_panel/coupons/',coupon_list_view,name='admin_couponlist'),
    path('admin_panel/coupons/disablecoupon/<id>/',disable_coupon_view,name='disablecoupon'),
    path('admin_panel/coupons/deletecoupon/<id>/',delete_coupon_view,name='deletecoupon'),
    #------------------------cart---------------------------------------
    path('cart/add_coupon_to_cart/',add_coupon_to_cart,name='addcoupontocart'),
    path('cart/remove_coupon_from_cart/',remove_coupon_from_cart),
    path('user_coupon_check/',check_user_coupon_in_cart),
    path('admin_panel/coupons/check_order/',check_order),
]
