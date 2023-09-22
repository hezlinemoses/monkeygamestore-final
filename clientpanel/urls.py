from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from clientpanel.views import (
home_view,
client_signup_view,
login_view,
order_detail_view,
verify_code_view,
logout_view,
send_verify_otp,
otp_login_view,
otp_login_verify,
game_detail_view,
blocked_view,
store_view,
account_view,
user_order_history,
order_cancel_view,
order_detail_view,
address_list_view,
address_edit_view,
address_delete_view,

)


urlpatterns = [
    path('',home_view,name='home'),
    path('signup/', client_signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('verify_otp/',verify_code_view,name='verification'),
    path('send_otp/',send_verify_otp,name='send_otp'),
    path('logout/',logout_view, name='logout'),
    path('otplogin/',otp_login_view,name='otplogin'),
    path('otplogin/verify/<id>/',otp_login_verify,name='otploginverify'),
    path('gamedetail/<id>/', game_detail_view,name='gamedetail'),
    path('blocked/',blocked_view,name="blocked"),
    path('store/',store_view,name='store'),
    #------------------------------------------------------------------------#
    path('account/',account_view,name='account'),
    path('account/orders/',user_order_history,name='orderhistory'),
    path('account/orders/<id>',order_detail_view, name='orderdetail'),
    path('account/orders/<id>/cancel',order_cancel_view,name='ordercancel'),
    path('account/address/',address_list_view,name='addresslist'),
    path('account/address/edit/<id>',address_edit_view,name='addressedit'),
    path('account/address/delete/<id>',address_delete_view,name='addressdelete'),
    
]