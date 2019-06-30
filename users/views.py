
import json

# Create your views here.
from django.shortcuts import render
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.views.generic.base import View
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import BaseUser,Student
from .forms import RegisterForm,LoginForm,ModifyPwdForm

class UserBackend(ModelBackend):
    """
    BaseUser authentication backend
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = BaseUser.objects.get(Q(username=username)|Q(email=username),Q(type=kwargs.get('user_type','')))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class RegisterView(View):
    """
    学生注册
    """
    def get(self,request):
        register_form = RegisterForm()
        return render(request,"register.html",{'register_form':register_form})

    def post(self,request):
        #register_form = RegisterForm(request.POST)
        dataPOST = json.loads(request.body)
        dataPOST['birthdate'] = dataPOST['birthdate'][0:10]
        dataPOST['enroll_time'] = dataPOST['enroll_time'][0:10]
        register_form = RegisterForm(dataPOST)
        if register_form.is_valid():
            email = dataPOST.get('email','')
            if Student.objects.filter(user__email=email):
                return render(request, "register.html",{"register_form": register_form, "msg": "该邮箱已注册"})
            password = dataPOST.get('password','')

            #创建BaseUser对象
            baseuser = BaseUser()
            baseuser.username = dataPOST.get('stu_id','')
            baseuser.password = make_password(password)
            baseuser.type = 1
            baseuser.email = email
            baseuser.save()

            #创建Student对象
            student = Student()
            student.user = baseuser
            student.stu_id = dataPOST.get('stu_id','')
            student.name = dataPOST.get('name','')
            student.department = dataPOST.get('department','')
            student.major = dataPOST.get('major','')
            student.enroll_time = dataPOST.get('enroll_time','')
            student.phone = dataPOST.get('phone','')
            student.birthdate = dataPOST.get('birthdate','')
            student.degree = dataPOST.get('degree','')
            student.address = dataPOST.get('address','')
            student.save()
            return HttpResponse(status=200)
            # return render(request,'login.html')

        else:
            # return render(request,'register.html',{"register_form":register_form})
            return HttpResponse(status=403)
class LoginView(View):
    """
    用户登录
    """
    def get(self,request):
        return render(request,'login.html',{})

    def post(self,request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = request.POST.get('username','')
            password = request.POST.get('password','')
            user_type = request.POST.get('type','')
            user = authenticate(username=username,password=password,user_type=user_type)
            if user is not None:
                login(request,user)
                return HttpResponseRedirect(reversed('index'))
            else:
                return render(request,'login.html',{'msg':'用户名或密码或用户类型错误！'})
        else:
            return render(request,'login.html',{'login_form':login_form})


class LogoutView(View):
    """
    用户登出
    """
    def get(self,request):
        logout(request)
        return HttpResponseRedirect(reversed('index'))

class UpdatePwdView(View):
    """
    用户在个人中心修改密码
    """
    def post(self,request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
           pwd1 = request.POST.get('pwd1','')
           pwd2 = request.POST.get('pwd2','')
           if pwd1 != pwd2:
               return HttpResponse("{'status':'fail','msg':'密码不一致'}",content_type='application/json')
           user = request.user
           user.password = make_password(pwd2)
           user.save()
           return HttpResponse("{'status':'success'}",content_type='application/json')
        else:
            return HttpResponse(json.dumps(modify_form.errors),content_type='application/json')


class SearchStudent(View):
    """
    模糊查找学生
    """
    def get(self,request):
        query = request.query_params.get('query_str','')
        query_set = Student.objects.filter(Q(stu_id__contains=query)|Q(name__contains=query))[:5]
        stu_dict = dict()
        stu_dict['stu'] = query_set
        return JsonResponse(stu_dict,safe=False)




def page_not_found(request,exception):
    """
    全局404处理函数
    :param request:
    :return:
    """
    from django.shortcuts import render_to_response
    response = render_to_response('404.html',{})
    response.status_code = 404
    return response

def page_error(request):
    """
    全局500处理函数
    :param request:
    :return:
    """
    from django.shortcuts import render_to_response
    response = render_to_response('500.html',{})
    response.status_code = 500
    return response