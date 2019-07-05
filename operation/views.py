from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import datetime, zipfile, tempfile, os
from wsgiref.util import FileWrapper

from competition.views import GetUserIdentitiy
from competition.models import Competition
from techworks.models import WorkInfo, Appendix
from users.models import Expert
from .models import Review
from TopCup.settings import MEDIA_ROOT
import json


# Create your views here.
def DownLoadZip(request):
    review = Review.objects.get(id = request.GET.get('id'))
    work = WorkInfo.objects.get(id=review.work_id)
    appendix_list = Appendix.objects.filter(work__work_id=work.work_id)
    temp = tempfile.TemporaryFile()
    archive = zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED)
    for appendix in appendix_list:
        target_file = os.path.join(MEDIA_ROOT, str(appendix.file)).replace('\\', '/')
        archive.write(target_file, appendix.filename)

    archive.close()
    data = temp.tell()
    temp.seek(0)
    wrapper = FileWrapper(temp)
    response = HttpResponse(wrapper, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=' + 'TEST' + '.zip' # 压缩包名称有问题
    response['Content-Length'] = data
    return response


def Judge(request):
    review = Review.objects.get(id=request.GET.get('id'))
    review.score = request.GET.get('score')
    review.comment = request.GET.get('comment')
    review.review_status = 3
    review.save()
    return render(request, 'ExpertReviewWorkList.html')


class ExpertReviewListView(View):
    def get(self, request):
        user_id = request.user.id
        review_invention_ret = []
        review_report_ret = []
        review_list = Review.objects.filter(expert__user_id=user_id)

        TAG_MAP = {
            2: "未评审",
            3: "已评审",
            4: "已提交"
        }

        for review in review_list:
            work = WorkInfo.objects.get(id=review.work_id)
            if work.work_type == 1:
                review_invention_ret.append({
                    'id': review.id,
                    'title': work.title,
                    'keywords': work.keywords,
                    'score': review.score,
                    'tag': TAG_MAP[review.review_status]
                })
            else:
                review_report_ret.append({
                    'id': review.id,
                    'title': work.title,
                    'keywords': work.keywords,
                    'score': review.score,
                    'tag': TAG_MAP[review.review_status]
                })

        paginator1 = Paginator(review_invention_ret, 10)  # 每页10条
        paginator2 = Paginator(review_report_ret, 10)
        total1 = len(review_invention_ret)
        total2 = len(review_report_ret)
        list1 = paginator1.page(1)
        list2 = paginator2.page(1)
        page = request.GET.get('page')

        user_name, user_identity = GetUserIdentitiy(request)
        return render(request, 'ExpertReviewWorkList.html', {'invention': review_invention_ret,
                                                             'report': review_report_ret,
                                                             'num1': list1.number, 'total1': total1,
                                                             'num2': list2.number, 'total2': total2,
                                                             'username': user_name, 'useridentity': user_identity})


class ExpertReviewView(View):
    def get(self, request):
        id = request.GET.get('id')
        username = request.user.username
        work = None
        show_list = []
        invest_list = []
        file_docu = []
        file_photo = []
        file_video = []
        if id is None:
            return HttpResponse(status=400)     #作品不存在

        else:
            review = Review.objects.get(id=id)
            work = WorkInfo.objects.get(id=review.work_id)

            if work.work_type == 1:
                show_list = json.loads(work.labels)['labels']
            else:
                invest_list = json.loads(work.labels)['labels']

            filelist = Appendix.objects.filter(work__work_id=work.work_id)
            for file in filelist:
                if file.appendix_type == 0:
                    file_docu.append({"name": file.filename, "url": file.file.url})
                elif file.appendix_type == 1:
                    file_photo.append({"name": file.filename, "url": file.file.url})
                elif file.appendix_type == 2:
                    file_video.append({"name": file.filename, "url": file.file.url})

        user_name, user_identity = GetUserIdentitiy(request)
        return render(request, 'ExpertReviewWork.html', {'work': work, 'id': review.id,
                                                         'score': review.score, 'comment':review.comment,
                                                         'show_list': show_list, 'invest_list': invest_list,
                                                         'docu': file_docu, 'photo': file_photo, 'video': file_video,
                                                         'username': user_name, 'useridentity': user_identity})

    def post(self, request):
        pass


    # @csrf_exempt
    # def show(request):
    #     user_name, user_identity = GetUserIdentitiy(request)
    #     work_id = request.GET.get('work_id')
    #     work = WorkInfo.objects.get(work_id=work_id)
    #     expert = Expert.objects.get(user__email=request.user.username)
    #     expert_id = expert.user.id
    #     # expert_id = request.GET.get('expert_id')
    #     try:
    #         review = Review.objects.filter(work=work, expert=expert)
    #         if len(review) > 0:
    #             review = review[0]
    #             if review.review_status == 0:  # 还没评过
    #                 return render(request, 'judgeWork.html',
    #                               {'status': 0, 'score': 50, 'expert_id': expert_id, 'work_id': work_id,
    #                                'useridentity': user_identity})
    #             else:  # 暂存或评价过
    #                 return render(request, 'judgeWork.html',
    #                               {'status': review.review_status, 'score': review.score, 'comment': review.comment,
    #                                'expert_id': expert_id, 'work_id': work_id, 'useridentity': user_identity})
    #         else:
    #             Review.objects.create(work=work, expert=expert, score=50, comment='', review_status=0,
    #                                   add_time='2019-07-02')
    #             return render(request, 'judgeWork.html',
    #                           {'status': 50, 'score': 0, 'expert_id': expert_id, 'work_id': work_id,
    #                            'useridentity': user_identity})
    #     except Exception as e:
    #         print(e)
    #         pass
    #


class AssignWorkListView(View):
    """
    展示待分配作品列表
    """
    def get(self,request):
        cpt_id = request.GET.get('cpt_id','')
        worklist_origin = WorkInfo.objects.all()
        WORKTYPE_MAP = {
            1: "科技发明制作",
            2: "调查报告和学术论文"
        }
        FIELD_MAP = {
            1: "A",
            2: "B",
            3: "C",
            4: "D",
            5: "E",
            6: "F",
        }
        worklist_ret = []
        for work in worklist_origin:
            worklist_ret.append({
                'work_id':work.work_id,
                'title':work.title,
                'work_type':WORKTYPE_MAP[work.work_type],
                'field':FIELD_MAP[work.field],
            })

        expertlist_origin = Expert.objects.all()
        expertlist_ret = []
        for expert in expertlist_origin:
            expertlist_ret.append({
                'expert_id':expert.user.id,
                'name':expert.name,
                'field':FIELD_MAP[expert.field],
                'email':expert.user.email,
            })

        user_name,user_identity = GetUserIdentitiy(request)
        return render(request,'assignwork_list.html',{'expertlist':expertlist_ret,'worklist':worklist_ret,'useridentity':user_identity,'username':user_name})


class AssignExpertView(View):
    """
    待分配专家
    """
    def get(self,request):
        pass

    def post(self,request):
        expert_list = request.POST.get('selected_expert')
        work_list = request.POST.get('selected_work')
        for expert_id in expert_list:
            for work_id in work_list:
                review = Review()
                review.work = work_id
                review.expert = expert_id
                review.add_time = datetime.date.today
                review.review_status = 0 #邮件刚刚发出的状态
                review.save()
        cpt_name = WorkInfo.objects.get(work_id=work_list[0]).registration.competition.title


        # ref：https://www.cnblogs.com/lovealways/p/6701662.html
        import smtplib
        from email.mime.text import MIMEText
        sender = '1102616394@qq.com'
        passwd = 'zkgiepqbxtrubahb'
        s = smtplib.SMTP_SSL('smtp.qq.com', 465)
        s.login(sender, passwd)
        for expert_id in expert_list:
            receiver = Expert.objects.get(user_id=expert_id).user.email
            subject = '邀请参加'+'\"'+cpt_name+'\"'+'作品评审'
            content = '这是email内容'
            msg = MIMEText(content)
            msg['Subject'] = subject
            msg['From'] = sender
            msg['To'] = receiver
            try:
                s.sendmail(sender,receiver,msg.as_string())
            except:
                pass
        s.quit()



