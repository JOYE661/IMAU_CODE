from django.http import JsonResponse
from django.db.models import F
from django.db import IntegrityError, transaction

# 导入 Order 对象定义
from  common.models import  Order,OrderMedicine


def addorder(request):
    info = request.params['data']

    # 从请求消息中 获取要添加订单的信息
    # 并且插入到数据库中

    with transaction.atomic():
        new_order = Order.objects.create(name=info['name'],
                                         customer_id=info['customerid'])

        batch = [OrderMedicine(order_id=new_order.id, medicine_id=mid, amount=1)
                 for mid in info['medicineids']]
        OrderMedicine.objects.bulk_create(batch)

    return JsonResponse({'ret': 0, 'id': new_order.id})


def listorder(request):
    qs = Order.objects \
        .annotate(
                customer_name=F('customer__name'),
                medicines_name=F('medicines__name')
        )\
        .values(
        'id', 'name', 'create_date',
        # 两个下划线，表示取customer外键关联的表中的name字段的值
        'customer_name',
        'medicines_name'
    )

    # 将 QuerySet 对象 转化为 list 类型
    retlist = list(qs)

    # 可能有 ID相同，药品不同的订单记录， 需要合并

    newlist = []
    id2order = {}
    for one in retlist:
        orderid = one['id']
        if orderid not in id2order:
            newlist.append(one)
            id2order[orderid] = one
        else:
            id2order[orderid]['medicines_name'] += ' | ' + one['medicines_name']

    return JsonResponse({'ret': 0, 'retlist': newlist})


from lib.handler import dispatcherBase

Action2Handler = {
    'list_order': listorder,
    'add_order': addorder,
}

def dispatcher(request):
    return  dispatcherBase(request, Action2Handler)