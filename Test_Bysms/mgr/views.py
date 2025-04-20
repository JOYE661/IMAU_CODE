from django.shortcuts import render
from django.http import HttpResponse
from Test_api.deepseek import deepseek
def listorders(request):
    ret=deepseek("评价一下你自己")
    str = f"{ret}"
    return HttpResponse(str)
# Create your views here.
def orders(request):
    return HttpResponse("下面是系统中所有的订单信息")


def medicines(request):
    return HttpResponse("下面是系统中所有的药物信息")
