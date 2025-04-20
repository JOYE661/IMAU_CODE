from django.urls import path
from mgr import customer,sign_in_out,medicine,order
from .import views
urlpatterns = [

    path('customers', customer.dispatcher),
    path('medicines', medicine.dispatcher),
    path('orders', order.dispatcher),
    path('deepseek/',views.listorders),

    path('signin', sign_in_out.signin),
    path('signout', sign_in_out.signout),
]