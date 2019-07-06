# -*-coding:utf-8 -*-
import datetime
import json
import os
import tempfile
import zipfile
from wsgiref.util import FileWrapper

from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import datetime, zipfile, tempfile, os
from wsgiref.util import FileWrapper
from django.utils.encoding import escape_uri_path
from django.views.generic.base import View

from TopCup.settings import MEDIA_ROOT
from competition.models import Competition
from competition.views import GetUserIdentitiy
from techworks.models import WorkInfo, Appendix
from users.models import Expert
from .models import Review

import hashlib, zlib
import pickle
import urllib
import base64


# Create your views here.

class CheckWorkListView(View):
    """
    展示待评审作品列表
    """
    def get(self,request):
        cpt_id = request.GET.get('cpt_id','')
        worklist_origin = WorkInfo.objects.filter(check_status=-1)
        # to do: 1.属于某个比赛的作品 2.
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
                'id':work.id,
                'work_id':work.work_id,
                'title':work.title,
                'work_type':WORKTYPE_MAP[work.work_type],
                'field':FIELD_MAP[work.field],
            })


        user_name,user_identity = GetUserIdentitiy(request)
        return render(request,'check_worklist.html',{'worklist':worklist_ret , 'useridentity':user_identity,'username':user_name})

    def post(self,request):

        work_list = request.POST.get('selected_work')
        work_list = json.loads(work_list)

        for work_id in work_list:
            work_i = WorkInfo.objects.get(work_id=work_id) #数据库是否存在work_id相同的多个比赛
            work_i.check_status = 1
            work_i.save()
        return JsonResponse({'Message':0})

def DownLoadZip(request):
    status = request.GET.get('status')
    if status == '0':
        review = Review.objects.get(id = request.GET.get('id'))
        work = WorkInfo.objects.get(id=review.work_id)
        id = review.id
    else:
        work = WorkInfo.objects.get(id = request.GET.get('id'))
        id = work.work_id

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
    filename = str(id) + '_' + work.title + '.zip'
    response['Content-Disposition'] = "attachment; filename*=utf-8''{}".format(escape_uri_path(filename))  # 压缩包名称有问题
    response['Content-Length'] = data
    return response


def DownloadBatchZip(request):
    status = request.GET.get('status')
    work_list = []
    id_list = json.loads(request.GET.get('id_list'))
    if status == '0':
        for id in id_list:
            review = Review.objects.get(id=id)
            work_list.append(WorkInfo.objects.get(id=review.work_id))
    else:
        for id in id_list:
            work_list.append(WorkInfo.objects.get(id=id))

    Temp = tempfile.TemporaryFile()
    Archive = zipfile.ZipFile(Temp, 'w', zipfile.ZIP_DEFLATED)
    for work in work_list:
        appendix_list = Appendix.objects.filter(work__work_id=work.work_id)
        temp = tempfile.TemporaryFile(dir=MEDIA_ROOT+'\\compressed', delete=False)
        archive = zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED)
        for appendix in appendix_list:
            target_file = os.path.join(MEDIA_ROOT, str(appendix.file)).replace('\\', '/')
            archive.write(target_file, appendix.filename)
        archive.close()
        temp.seek(0)
        target_file = os.path.join(MEDIA_ROOT + '/compressed', str(temp.name)).replace('\\', '/')
        Archive.write(target_file, str(work.title)+'.zip')

    Archive.close()
    data = Temp.tell()
    Temp.seek(0)
    wrapper = FileWrapper(Temp)
    response = HttpResponse(wrapper, content_type='application/zip')
    filename = 'TopCup作品集.zip'
    response['Content-Disposition'] = "attachment; filename*=utf-8''{}".format(escape_uri_path(filename))
    response['Content-Length'] = data
    return response


def Judge(request):
    review = Review.objects.get(id=request.GET.get('id'))
    review.score = request.GET.get('score', review.score)
    review.comment = request.GET.get('comment', review.comment)
    review.review_status = 3
    review.save()
    return render(request, 'ExpertReviewWorkList.html')


def sumbitReview(request):
    user_id = request.user.id
    review_list = Review.objects.filter(expert__user_id=user_id)
    status = 1
    for review in review_list:
        if review.review_status == 2:
            status = 0
            break
    if status == 1:
        for review in review_list:
            review.review_status = 4
            review.save()

        # update work review status
        review_list = Review.objects.filter(expert__user_id=user_id)
        for review in review_list:
            work_reviews = Review.objects.filter(work=review.work)
            review_finish = 1
            if len(work_reviews) < 3:
                review_finish = 0
            else:
                for r in work_reviews:
                    if r.review_status != 4:
                        review_finish = 0
                        break
            if review_finish == 1:
                review.work.review_status = 1
                review.work.save()

    ret={'status': status}
    return JsonResponse(ret)


def NextReviewWork(request):
    review = Review.objects.get(id=request.GET.get('id'))
    type = WorkInfo.objects.get(id=review.work_id).work_type
    expertid = review.expert_id
    review_list = Review.objects.filter(Q(work__work_type=type) & Q(expert__user_id=expertid) & Q(review_status=2))
    if len(review_list):
        ret = {'nextid': review_list[0].id}
    else:
        ret = {'nextid': 0}
    return JsonResponse(ret)


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
                    'comment':review.comment,
                    'tag': TAG_MAP[review.review_status]
                })
            else:
                review_report_ret.append({
                    'id': review.id,
                    'title': work.title,
                    'keywords': work.keywords,
                    'score': review.score,
                    'comment': review.comment,
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
        show = []
        invest = []
        file_docu = []
        file_photo = []
        file_video = []
        SHOW_MAP = {1: "实物、产品", 2: "模型", 3: "图纸", 4: "磁盘", 5: "现场演示", 6: "图片", 7: "录像", 8: "样品"}
        INVEST_MAP = {1: "走访", 2: "问卷", 3: "现场采访", 4: "人员介绍", 5: "个别交谈", 6: "亲临实践", 7: "会议",
                      8: "图片、照片", 9: "书报刊物", 10: "统计报表", 11: "影视资料", 12: "文件", 13: "集体组织", 14: "自发",
                      15: "其他"}
        if id is None:
            return HttpResponse(status=400)     #作品不存在

        else:
            show_list = []
            invest_list = []
            review = Review.objects.get(id=id)
            work = WorkInfo.objects.get(id=review.work_id)

            if work.work_type == 1:
                show_list = json.loads(work.labels)['labels']
                for i in show_list:
                    show.append(SHOW_MAP[int(i)])
            else:
                invest_list = json.loads(work.labels)['labels']
                for i in show_list:
                    invest.append(INVEST_MAP[int(i)])
            filelist = Appendix.objects.filter(work__work_id=work.work_id)
            for file in filelist:
                if file.appendix_type == 1:
                    file_docu.append({"name": file.filename, "url": file.file.url})
                elif file.appendix_type == 2:
                    file_photo.append({"name": file.filename, "url": file.file.url})
                elif file.appendix_type == 3:
                    file_video.append({"name": file.filename, "url": file.file.url})

        user_name, user_identity = GetUserIdentitiy(request)
        return render(request, 'ExpertReviewWork.html', {'work': work, 'id': review.id,
                                                         'score': review.score, 'comment':review.comment,
                                                         'tag': review.review_status,
                                                         'show_list': show, 'invest_list': invest,
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
        reviewed_worklist = list(Review.objects.all().values_list('work__work_id', flat=True))
        worklist_origin = WorkInfo.objects.filter(registration__competition__id=cpt_id).exclude(work_id__in=reviewed_worklist)
        # to do: 1.属于某个比赛的作品 2.
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

        # 专家拒绝了待处理
        expertlist_origin = Expert.objects.all().exclude(user__id__in=
            Review.objects.filter(review_status__lt=4).values_list('expert__user__id', flat=True))
        expertlist_ret = []
        for expert in expertlist_origin:
            expertlist_ret.append({
                'expert_id':expert.user.id,
                'name':expert.name,
                'field':FIELD_MAP[expert.field],
                'email':expert.user.email,
            })

        user_name,user_identity = GetUserIdentitiy(request)
        return render(request,'assignwork_list.html',{'expertlist':expertlist_ret, 'worklist':worklist_ret , 'useridentity':user_identity,'username':user_name})

class AssignExpertView(View):
    """
    待分配专家
    """
    def get(self,request):
        pass

    def post(self,request):
        expert_list = json.loads(request.body)
        expert_list = expert_list['selected_expert']
        work_list = json.loads(request.body)
        work_list = work_list['selected_work']
        cpt_id = json.loads(request.body)['cpt_id']
        cpt_title = Competition.objects.get(id=cpt_id).title

        for expert_id in expert_list:
            for work_id in work_list:
                work_i = WorkInfo.objects.get(work_id=work_id) #数据库是否存在work_id相同的多个比赛
                expert_i = Expert.objects.get(user_id=expert_id)

                review = Review()
                review.work = work_i
                review.expert = expert_i
                review.add_time = datetime.date.today()
                review.score = -1
                review.review_status = 0 #邮件刚刚发出的状态
                review.save()
        cpt_name = WorkInfo.objects.get(work_id=work_list[0]).registration.competition.title


        # ref：https://www.cnblogs.com/lovealways/p/6701662.html
        import smtplib
        from email.mime.text import MIMEText
        sender = 'topcup2019@163.com'
        passwd = '123456zxcvbn'
        host = request.get_host()
        s = smtplib.SMTP_SSL('smtp.163.com', 465)
        s.login(sender, passwd)
        for expert_id in expert_list:
            arg = [expert_id, cpt_id, 1]
            hash, enc = self.encode_data(arg)
            acc_url = 'https://' + host + '/invitation/?hash=' + hash + '&enc=' + enc
            arg = [expert_id, cpt_id, 0]
            hash, enc = self.encode_data(arg)
            def_url = 'https://' + host + '/invitation/?hash=' + hash + '&enc=' + enc
            receiver = Expert.objects.get(user_id=expert_id).user.email
            subject = '邀请参加科技竞赛作品评审'
            content = "<p>尊敬的" + '\"' + Expert.objects.get(
                user_id=expert_id).name + '\"' + "：</p>" + "<p>邀请您参与TopCup\"" + cpt_title + "\"作品评审</p>" + "<p><a href=" + acc_url + ">接受</a></p> <p><a href=" + def_url + ">拒绝</a></p>"
            msg = MIMEText(content, "html", "utf-8")
            msg['Subject'] = subject
            msg['From'] = sender
            msg['To'] = receiver
            try:
                s.sendmail(sender, receiver, msg.as_string())
            except:
                return JsonResponse({'Message': 1})
                pass
        s.quit()
        return JsonResponse({'Message': 0})

    def encode_data(self, data):
        """Turn `data` into a hash and an encoded string, suitable for use with `decode_data`."""
        compressed_text = zlib.compress(pickle.dumps(data, 0))
        text = base64.b64encode(compressed_text).decode().replace('\n', '')
        m = hashlib.md5(str.encode('{}{}'.format('yankun', text))).hexdigest()[:12]
        return m, text

class ExptreviewListView(View):
    """
    展示已分配的专家-作品对
    """
    def get(self, request):

        FIELD_MAP = {
            1: "A",
            2: "B",
            3: "C",
            4: "D",
            5: "E",
            6: "F",
        }

        cpt_id = request.GET.get('cpt_id','')
        user_name,user_identity = GetUserIdentitiy(request)
        context = {}
        context['username'] = user_name
        context['useridentity'] = user_identity

        # 从Review表中选出该比赛的review
        reviews = Review.objects.all()
        review_ret = []
        for review_i in reviews:
            review_ret.append(
                {
                    'init_date': str(review_i.add_time),
                    'expert_id': review_i.expert.user.id,
                    'expert_name': review_i.expert.name,
                    'expert_field': review_i.expert.field,
                    'email': review_i.expert.user.email,
                    'work_id': review_i.work.work_id,
                    'work_name': review_i.work.title,
                    'work_type':review_i.work.work_type,
                    'work_field': review_i.work.field,
                    'review_state': review_i.review_status
                }
            )
        context['review_ret'] = review_ret

        #待选专家
        expertlist_origin = Expert.objects.all().exclude(user__id__in=
        Review.objects.all().values_list('expert__user__id', flat=True))
        expertlist_ret = []
        for expert in expertlist_origin:
            expertlist_ret.append({
                'expert_id':expert.user.id,
                'name':expert.name,
                'field':FIELD_MAP[expert.field],
                'email':expert.user.email,
            })
        context['expertlist'] = expertlist_ret

        return render(request, 'exptreview_list.html', context)

class DefenseWorkListView(View):
    """
    展示待遴选作品列表
    """
    def get(self,request):
        cpt_id = request.GET['cptid']
        print(cpt_id)
        Cpt=Competition.objects.get(id=cpt_id)
        worklist_origin = WorkInfo.objects.filter(registration__competition=Cpt)
        #求每个作品的平均分并填表
        # scorelist=Review.objects.values('work').annotate(avgscore=Avg('score')).values("work","avgscore")
        # worklist=WorkInfo.objects.all()
        # for i in worklist:
        #     try:
        #         i.avg_score=Decimal(scorelist.get(work = i)['avgscore']).quantize(Decimal('0.00'))
        #     except:
        #         i.avg_score = 0
        #     i.save()


            # i.avg_score=scorelist.filter('work' == i.work_id)
            # i.save()

        # to do: 1.属于某个比赛的作品 2.
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
            if work.if_defense==0:
                worklist_ret.append({
                    'work_id':work.work_id,
                    'title':work.title,
                    'work_type':WORKTYPE_MAP[work.work_type],
                    'field':FIELD_MAP[work.field],
                    'avgscore':work.avg_score
                })
        user_name,user_identity = GetUserIdentitiy(request)
        return render(request,'defensework_list.html',{ 'worklist':worklist_ret , 'useridentity':user_identity,'username':user_name,'cpt_id':cpt_id})

    def post(self, request):
        defenseWorkList = json.loads(request.body)
        with transaction.atomic():
            for item in defenseWorkList:
                work = WorkInfo.objects.get(work_id=item.get("work_id"))
                work.if_defense = True
                work.save()
        # print(request.data)

        return JsonResponse({'Message': 0})

class ExptTreetableView(View):
    """
    以专家为主体展示已分配到某个专家的作品列表
    """
    def get(self, request):
        FIELD_MAP = {
            1: "A",
            2: "B",
            3: "C",
            4: "D",
            5: "E",
            6: "F",
        }

        cpt_id = request.GET.get('cpt_id','')
        user_name,user_identity = GetUserIdentitiy(request)
        context = {}
        context['username'] = user_name
        context['useridentity'] = user_identity

        # 从Review表中选出该比赛的review
        reviews = Review.objects.all()
        expt_tree_ret = {}

        # 以专家ID为key, value为专家信息和需要评审的作品列表
        for review_i in reviews:
            temp_expt_id = review_i.expert.user.id
            if temp_expt_id in expt_tree_ret.keys():
                expt_tree_ret[temp_expt_id]['works'].append(
                    {
                        'work_id': review_i.work.work_id,
                        'work_name': review_i.work.title,
                        'work_type':review_i.work.work_type,
                        'work_field': review_i.work.field,
                        'review_state': review_i.review_status,
                    }
                )
            else:
                expt_tree_ret[temp_expt_id] = {
                    'init_date': str(review_i.add_time),
                    'expert_id': review_i.expert.user.id,
                    'expert_name': review_i.expert.name,
                    'expert_field': review_i.expert.field,
                    'email': review_i.expert.user.email,
                    'expert_state': review_i.review_status,
                    'works':[]
                }
                expt_tree_ret[temp_expt_id]['works'].append(
                    {
                        'work_id': review_i.work.work_id,
                        'work_name': review_i.work.title,
<<<<<<< HEAD
                        'work_type':review_i.work.work_type,
=======
                        'work_type': review_i.work.work_type,
>>>>>>> 962584e276e064e865d126ebcaf94b8ae808bc5b
                        'work_field': review_i.work.field,
                        'review_state': review_i.review_status,
                    }
                )

        #字典转换为列表
        expt_tree_ret = list(expt_tree_ret.values())
        context['expt_tree_ret'] = expt_tree_ret

        #待选专家
        expertlist_origin = Expert.objects.all().exclude(user__id__in=
            Review.objects.all().values_list('expert__user__id', flat=True))
        expertlist_ret = []
        for expert in expertlist_origin:
            expertlist_ret.append({
                'expert_id':expert.user.id,
                'expert_name':expert.name,
                'expert_field':FIELD_MAP[expert.field],
                'email':expert.user.email,
            })
        context['expertlist'] = expertlist_ret

        return render(request, 'expert_treetable.html', context)

class ReassignExpertView(View):
    """
    重新分配专家
    """

    def get(self,request):
        pass

    def post(self,request):
        originExpert_work = json.loads(request.body)['originExpert_work']
        originExpert_expt = json.loads(request.body)['originExpert_expt']
        cpt_id = json.loads(request.body)['cpt_id']
        cpt_title = Competition.objects.get(id=cpt_id).title
        # 为review更换专家
        try:
            for origin_expert_id in originExpert_expt.keys():
                # 用ID拿expert
                new_expert_id = originExpert_expt[origin_expert_id]
                new_expert = Expert.objects.get(user__id=new_expert_id)
                origin_expert = Expert.objects.get(user__id=origin_expert_id)

<<<<<<< HEAD
            # try:
            for work_id in originExpert_work[origin_expert_id]:
                review = Review.objects.get(Q(expert=origin_expert) & Q(work__work_id=work_id))
                
                review.expert = new_expert
                review.review_status = 0
                review.save()
            # except:
            #     return JsonResponse({'Message':1})
            #     pass

        # ref：https://www.cnblogs.com/lovealways/p/6701662.html
        # import smtplib
        # from email.mime.text import MIMEText
        # sender = 'topcup2019@163.com'
        # passwd = '123456zxcvbn'
        # s = smtplib.SMTP_SSL('smtp.163.com', 465)
        # s.login(sender, passwd)
        # for expert_id in expert_list:
        #     receiver = Expert.objects.get(user_id=expert_id).user.email
        #     subject = '邀请参加'+'\"'+cpt_name+'\"'+'作品评审'
        #     content = '这是email内容'
        #     msg = MIMEText(content)
        #     msg['Subject'] = subject
        #     msg['From'] = sender
        #     msg['To'] = receiver
        #     try:
        #         s.sendmail(sender,receiver,msg.as_string())
        #     except:
        #         return JsonResponse({'Message':1})
        #         pass
        # s.quit()
=======
                for work_id in originExpert_work[origin_expert_id]:
                    work = WorkInfo.objects.get(work_id=work_id)
                    if Review.objects.filter(expert=new_expert, work=work).exists():
                        continue
                    else:
                        review = Review.objects.get(expert=origin_expert, work=work)
                        review.expert = new_expert
                        review.review_status = 0
                        review.save()

        except Exception as e:
            print(e)
            return JsonResponse({'Message':1})
            pass

        # ref：https://www.cnblogs.com/lovealways/p/6701662.html
        import smtplib
        from email.mime.text import MIMEText
        sender = 'topcup2019@163.com'
        passwd = '123456zxcvbn'
        host = request.get_host()
        s = smtplib.SMTP_SSL('smtp.163.com', 465)
        s.login(sender, passwd)
        for expert_id in originExpert_expt.values():
            arg = [expert_id, cpt_id, 1]
            hash, enc = self.encode_data(arg)
            acc_url = 'https://' + host + '/invitation/?hash=' + hash + '&enc=' + enc
            arg = [expert_id, cpt_id, 0]
            hash, enc = self.encode_data(arg)
            def_url = 'https://' + host + '/invitation/?hash=' + hash + '&enc=' + enc
            receiver = Expert.objects.get(user_id=expert_id).user.email
            subject = '邀请参加科技竞赛作品评审'
            content = "<p>尊敬的" + '\"' + Expert.objects.get(
                user_id=expert_id).name + '\"' + "：</p>" + "<p>邀请您参与TopCup\"" + cpt_title + "\"作品评审</p>" + "<p><a href=" + acc_url + ">接受</a></p> <p><a href=" + def_url + ">拒绝</a></p>"
            msg = MIMEText(content, "html", "utf-8")
            msg['Subject'] = subject
            msg['From'] = sender
            msg['To'] = receiver
            try:
                s.sendmail(sender, receiver, msg.as_string())
            except:
                return JsonResponse({'Message': 1})
                pass
        s.quit()
<<<<<<< HEAD
>>>>>>> 962584e276e064e865d126ebcaf94b8ae808bc5b
        return JsonResponse({'Message':0})
=======
        return JsonResponse({'Message': 0})

    def encode_data(self, data):
        """Turn `data` into a hash and an encoded string, suitable for use with `decode_data`."""
        compressed_text = zlib.compress(pickle.dumps(data, 0))
        text = base64.b64encode(compressed_text).decode().replace('\n', '')
        m = hashlib.md5(str.encode('{}{}'.format('yankun', text))).hexdigest()[:12]
        return m, text


class InvitationView(View):
    def get(self, request):
        hash = request.GET.get('hash', '')
        enc = request.GET.get('enc', '')
        data = self.decode_data(hash=hash, enc=enc)
        expert_id = data[0]
        cpt_id = data[1]
        acc = data[2]
        if acc == 0:
            finded_reviews = Review.objects.filter(expert__user__id=expert_id, work__registration__competition__id=cpt_id)
            for review in finded_reviews:
                review.review_status = 1
                review.save()
            return render(request, 'refuse_review.html')
        elif acc == 1:
            expert = Expert.objects.get(user__id=expert_id)
            finded_reviews = Review.objects.filter(expert=expert, work__registration__competition__id=cpt_id)
            for review in finded_reviews:
                review.review_status = 2
                review.save()
            return render(request, "login.html", { 'expert_email': expert.user.email ,'expert_activated':~expert.activated})

    def decode_data(self, hash, enc):
        """The inverse of `encode_data`."""
        text = urllib.parse.unquote(enc)
        m = hashlib.md5(str.encode('{}{}'.format('yankun', text))).hexdigest()[:12]
        if m != hash:
            raise Exception("Bad hash!")
        data = pickle.loads(zlib.decompress(base64.b64decode(text)))
        return data
>>>>>>> db9310d54474a412fec8124ff50c212198fbc763
