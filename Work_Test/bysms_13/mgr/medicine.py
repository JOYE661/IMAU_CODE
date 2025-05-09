from django.http import JsonResponse


import traceback

# 导入 Medicine 对象定义
from  common.models import  Medicine

from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q

from django_redis import get_redis_connection
from bysms import settings
import json
# 获取一个和Redis服务的连接
rconn = get_redis_connection("default")

def listmedicine(request):
    try:
        # 查看是否有 关键字 搜索 参数
        keywords = request.params.get('keywords',None)
        # 要获取的第几页
        pagenum = request.params['pagenum']
        # 每页要显示多少条记录
        pagesize = request.params['pagesize']


        # 先看看缓存中是否有
        cacheField = f"{pagesize}|{pagenum}|{keywords}" # 缓存 field

        cacheObj = rconn.hget(settings.CK.MedineList,
                             cacheField)


        # 缓存中有，需要反序列化
        if cacheObj:
            print('缓存命中')
            retObj = json.loads(cacheObj)


        # 如果缓存中没有，再去数据库中查询
        else:
            print('缓存中没有')

            # 返回一个 QuerySet 对象 ，包含所有的表记录
            qs = Medicine.objects.values().order_by('-id')

            if keywords:
                conditions = [Q(name__contains=one) for one in keywords.split(' ') if one]
                query = Q()
                for condition in conditions:
                    query &= condition
                qs = qs.filter(query)


            # 使用分页对象，设定每页多少条记录
            pgnt = Paginator(qs, pagesize)

            # 从数据库中读取数据，指定读取其中第几页
            page = pgnt.page(pagenum)

            # 将 QuerySet 对象 转化为 list 类型
            retlist = list(page)

            retObj = {'ret': 0, 'retlist': retlist,'total': pgnt.count}

            # 存入缓存
            rconn.hset(settings.CK.MedineList,
                       cacheField,
                       json.dumps(retObj))


        # total指定了 一共有多少数据
        return JsonResponse(retObj)

    except EmptyPage:
        return JsonResponse({'ret': 0, 'retlist': [], 'total': 0})

    except:
        print(traceback.format_exc())
        return JsonResponse({'ret': 2,  'msg': f'未知错误\n{traceback.format_exc()}'})


def addmedicine(request):

    info    = request.params['data']

    # 从请求消息中 获取要添加客户的信息
    # 并且插入到数据库中
    medicine = Medicine.objects.create(name=info['name'] ,
                            sn=info['sn'] ,
                            desc=info['desc'])


    # 同时删除整个 medicine 缓存数据
    # 因为不知道这个添加的药品会影响到哪些列出的结果
    # 只能全部删除
    rconn.delete(settings.CK.MedineList)

    return JsonResponse({'ret': 0, 'id':medicine.id})


def modifymedicine(request):

    # 从请求消息中 获取修改客户的信息
    # 找到该客户，并且进行修改操作

    medicineid = request.params['id']
    newdata    = request.params['newdata']

    try:
        # 根据 id 从数据库中找到相应的客户记录
        medicine = Medicine.objects.get(id=medicineid)
    except Medicine.DoesNotExist:
        return  {
                'ret': 1,
                'msg': f'id 为`{medicineid}`的药品不存在'
        }


    if 'name' in  newdata:
        medicine.name = newdata['name']
    if 'sn' in  newdata:
        medicine.sn = newdata['sn']
    if 'desc' in  newdata:
        medicine.desc = newdata['desc']

    # 注意，一定要执行save才能将修改信息保存到数据库
    medicine.save()

    # 同时删除整个 medicine 缓存数据
    # 因为不知道这个修改的药品会影响到哪些列出的结果
    # 只能全部删除
    rconn.delete(settings.CK.MedineList)

    return JsonResponse({'ret': 0})


def deletemedicine(request):

    medicineid = request.params['id']

    try:
        # 根据 id 从数据库中找到相应的药品记录
        medicine = Medicine.objects.get(id=medicineid)
    except Medicine.DoesNotExist:
        return  {
                'ret': 1,
                'msg': f'id 为`{medicineid}`的客户不存在'
        }

    # delete 方法就将该记录从数据库中删除了
    medicine.delete()

    # 同时删除整个 medicine 缓存数据
    # 因为不知道这个删除的药品会影响到哪些列出的结果
    # 只能全部删除
    rconn.delete(settings.CK.MedineList)


    return JsonResponse({'ret': 0})



from lib.handler import dispatcherBase

Action2Handler = {
    'list_medicine': listmedicine,
    'add_medicine': addmedicine,
    'modify_medicine': modifymedicine,
    'del_medicine': deletemedicine,
}

def dispatcher(request):
    return dispatcherBase(request, Action2Handler)