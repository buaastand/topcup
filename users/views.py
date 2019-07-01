from django.shortcuts import render
from users.models import Expert
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from users import models
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import xlrd #excel读工具
# Create your views here.
class ExpertManage():
    @csrf_exempt
    # 展示专家列表，允许上传文件添加专家，当和数据库中的专家邮箱重复时跳过
    def list(request):
        experts = Expert.objects.all()
        total = len(experts)
        paginator = Paginator(experts, 15)  # 每页15条
        list = paginator.page(1)
        page = request.GET.get('page')
        try:
            list = paginator.page(page)  # list为Page对象！
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            list = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            list = paginator.page(paginator.num_pages)

        if request.method == 'POST':
            f = request.FILES.get('file')
            excel_type = f.name.split('.')[1]
            if excel_type in ['xlsx', 'xls']:
                # 开始解析上传的excel表格
                wb = xlrd.open_workbook(filename=None, file_contents=f.read())
                table = wb.sheets()[0]
                rows = table.nrows  # 总行数
                # 要求导入的表必须是按照邮箱、姓名、领域的顺序存储，第一行是表头，不读入数据库
                for i in range(1, rows):
                    try:
                        # with transaction.atomic():  # 控制数据库事务交易
                        rowVlaues = table.row_values(i)
                        # major = models.Expert.objects.filter(name=rowVlaues[0]).first()
                        email = rowVlaues[0]
                        user = models.BaseUser.objects.create(type=3, email=email, username=email, password=email)
                        models.Expert.objects.create(user=user, name=rowVlaues[1], field=int(rowVlaues[2]))
                    except Exception as e:
                        print('解析excel文件或者数据插入错误')
                        print(e)
                        pass
                return render(request, 'expert-manage.html', {'message': '导入成功'})
            else:
                print('上传文件类型错误！')
                return render(request, 'expert-manage.html', {'message': '导入失败'})
        return render(request, "expert-manage.html", {'data': list, 'total':total})

    @csrf_exempt
    def expert_detail(request):
        # 修改专家信息时先获取原来的专家信息
        if request.method == 'POST':
            id = request.POST.get('id')
            print(id)
            expert_detail = models.Expert.objects.get(user_id=id)
            email = expert_detail.user.email
            name = expert_detail.name
            field = expert_detail.field

            return JsonResponse({'id': id, 'name': name, 'field': field, 'email':email})
        return JsonResponse({'message':"获取专家信息"})

    @csrf_exempt
    def change(request):
        # 修改专家信息
        if request.method == 'POST':
            id = request.POST.get('id')
            changed_email = request.POST.get('changed_email')
            changed_name = request.POST.get('changed_name')
            changed_field = request.POST.get('changed_field')
            try:
                expert = models.Expert.objects.get(user_id=id)
                user = models.BaseUser.objects.get(id=id)
                user.email = changed_email
                expert.name = changed_name
                expert.field = changed_field
                user.save()
                expert.save()
            except:
                return JsonResponse({'Message': "修改失败"})
            return JsonResponse({'Message': "修改成功"})
        return JsonResponse({'message': "修改专家信息"})

    @csrf_exempt
    def delete_expert(request):
        # 删除专家信息
        if request.method == 'POST':
            id = request.POST.get('id')
            try:
                models.Expert.objects.get(user_id=id).delete()
            except:
                return JsonResponse({'Message': "删除失败"})
            return JsonResponse({'Message': "删除成功"})
        return JsonResponse({'Message': "删除专家信息"})