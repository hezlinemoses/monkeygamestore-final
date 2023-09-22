from django.urls import path
from .views import completed_order_list_view

urlpatterns = [
    path('admin_panel/salesreport/',completed_order_list_view,name='salesreport'),
]
