from django.shortcuts import render
from django.http import HttpResponse
# 导入 Customer 对象定义
from  common.models import  Customer
from Test_api.deepseek import deepseek

# def listorders(request):
#     ret=deepseek("查询一下食品的各国关税并评估一下")
#     str = f"{ret}"
#     return HttpResponse(str)
# # def listorders(request):
# #     return HttpResponse("下面是系统中所有的订单信息。。。")
import markdown
from django.http import HttpResponse
from django.core.cache import cache
def listorders(request):
    cached_data = cache.get('cached_tariff_data')
    if cached_data:
        return HttpResponse(cached_data)
    
    try:
        raw_data = deepseek("查询一下中美日各国食品关税")
        # 转换 Markdown 为 HTML（根据 API 返回格式选择）
        html_data = markdown.markdown(raw_data)
        # 或直接处理换行：html_data = raw_data.replace('\n', '<br>')
        
        # 添加基本样式
        styled_html = f"""
            <div style="
                padding: 20px;
                margin: 20px auto;
                max-width: 800px;
                background: #f9f9f9;
                border-radius: 8px;
            ">
                {html_data}
            </div>
        """
        cache.set('cached_tariff_data', styled_html, 3600)  # 缓存1小时
        return HttpResponse(styled_html)
    except Exception as e:
        return HttpResponse("<div style='color: red'>数据加载失败，请稍后重试。</div>")
    
# 先定义好HTML模板
html_template = '''
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
table {
    border-collapse: collapse;
}
th, td {
    padding: 8px;
    text-align: left;
    border-bottom: 1px solid #ddd;
}
</style>
</head>
<body>
    <table>
    <tr>
    <th>id</th>
    <th>姓名</th>
    <th>电话号码</th>
    <th>地址</th>
    </tr>

    
    {% for customer in customers %}
      <tr>
      {% for name, value in customer.items %}
      
      <td>{{ value }}</td>
      
      {% endfor %}
      </tr>
    {% endfor %}

    </table>
</body>
</html>
'''


from django.template import engines
django_engine = engines['django']
template = django_engine.from_string(html_template)

def listcustomers(request):
    # 返回一个 QuerySet 对象 ，包含所有的表记录
    qs = Customer.objects.values()

    # 检查url中是否有参数phonenumber
    ph =  request.GET.get('phonenumber',None)

    # 如果有，添加过滤条件
    if ph:
        qs = qs.filter(phonenumber=ph)

    # 传入渲染模板需要的参数
    rendered = template.render({'customers':qs})

    return HttpResponse(rendered)







