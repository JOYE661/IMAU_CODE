from django.urls import path
from .import views
from sales.views import listorders,listcustomers

urlpatterns = [
    path('deepseek/',views.listorders),

    path('orders/', listorders),
    path('customers/', listcustomers),
]