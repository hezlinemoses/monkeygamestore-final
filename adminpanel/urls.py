from urllib.parse import urlparse

from django.urls import path
from adminpanel import views
from adminpanel.views import (admin_dashboard_view,admin_login_view,admin_logout_view,
admin_user_type_view,admin_customer_list_view,customer_block_view,order_list_view,
order_detail_view,order_weekly,order_monthly,revenue_weekly,revenue_monthly)
from products.views import (admin_category_list_view,admin_addcategory_view,admin_category_edit_view,admin_addgame_view,admin_listgame_view,admin_editgame_view,
                            admin_category_disable,subcategory_add_view,game_block_view,delete_category,delete_game)

urlpatterns = [
    path('', admin_dashboard_view, name='admin_dashboard'),
    path('login/', admin_login_view, name='admin_login'),
    path('logout/', admin_logout_view, name='admin_logout'),

    #---------------------------User/customer/staff-----------------------------

    path('users',admin_user_type_view, name='admin_user_type'),
    path('users/customers',admin_customer_list_view, name='customer_list'),
    path('users/customers/<id>/block/',customer_block_view, name='blockcustomer'),
  


    #---------------------------Category----------------------------------------------

    path('categories/',admin_category_list_view, name='admin_categorylist'),
    path('categories/addcategory/',admin_addcategory_view, name='admin_addcategory'),
    path('categories/<slug>/edit/',admin_category_edit_view, name='admin_editcategory'),
    path('categories/<slug>/disable/',admin_category_disable, name='disablecategory'),
    path('categories/<slug>/addsubcategory/',subcategory_add_view, name='add_subcategory'),
    path('categories/<slug>/delete/',delete_category,name='deletecategory'),




    #---------------------------Game-------------------------------------------------
    path('games/addgame/',admin_addgame_view,name='admin_addgame'),
    path('games/',admin_listgame_view,name='admin_gamelist'),
    path('games/<id>/edit/',admin_editgame_view,name='admin_editgame'),
    path('games/<id>/disable/',game_block_view,name='disablegame'),
    path('games/<id>/delete/',delete_game,name='deletegame'),
    
    # path('users/admins', admin_staff_list_view,name ='admin_staff_list_view'),

    #------------------------------Orders-----------------------------------------
    path('orders/',order_list_view,name='admin_orderlist'),
    path('orders/detail/<id>/',order_detail_view,name = 'admin_orderdetail'),

    #------------------------------Charts---------------------------------------
    path('weeklyorders/',order_weekly,name='weeklyorders'),
    path('monthlyorders/',order_monthly,name='monthlyorders'),
    path('weeklyrevenue/',revenue_weekly,name='weeklyrevenue'),
    path('monthlyrevenue/',revenue_monthly,name='monthlyrevenue'),

]



