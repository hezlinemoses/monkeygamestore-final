from django.urls import path
from .views import(category_offer_add_view, change_game_option,
change_valid_till_field,
change_category_option,
edit_category_offer,
product_offer_add_view,
change_game_option,
change_valid_till_field_game,
edit_product_offer,
offer_list_view,
category_offer_delete_view,
category_offer_disable_view,
product_offer_delete_view,
product_offer_disable_view
)

urlpatterns = [
    path('admin_panel/offers/addcategoryoffer/',category_offer_add_view,name='addcategoryoffer'),
    path('admin_panel/offers/addcategoryoffer/change_valid_till/',change_valid_till_field),
    path('admin_panel/offers/addcategoryoffer/change_category_option/',change_category_option),
    path('admin_panel/offers/editcategoryoffer/<id>/',edit_category_offer,name = 'editcategoryoffer'),
    path('admin_panel/offers/deletecategoryoffer/<id>',category_offer_delete_view,name = 'deletecategoryoffer'),
    path('admin_panel/offers/disablecategoryoffer/<id>',category_offer_disable_view,name='disablecategoryoffer'),
    
    #-----------------------------------Product Offer--------------------------------------------------#
    path('admin_panel/offers/addproductoffer/',product_offer_add_view, name='addproductoffer'),
    path('admin_panel/offers/addproductoffer/change_game_option/',change_game_option),
    path('admin_panel/offers/addproductoffer/change_valid_till/',change_valid_till_field_game),
    path('admin_panel/offers/editproductoffer/<id>/',edit_product_offer, name='editproductoffer'),
    path('admin_panel/offers/deleteproductoffer/<id>',product_offer_delete_view,name = 'deleteproductoffer'),
    path('admin_panel/offers/disableproductoffer/<id>',product_offer_disable_view,name='disableproductoffer'),

    #-----------------------------------------------------------------------------------------------------#
    path('admin_panel/offers/',offer_list_view,name='offerlist'),

    
]
