from django.shortcuts import render
from django.views import View
from techworks.models import WorkInfo
from competition.views import GetUserIdentitiy
# Create your views here.
class ReviewWorkListView(View):
    # @login_required(login_url='/login/')
    def get(self, request):
        # if request.GET.get('workid', None) is None:
        #     WorkInfo.objects.create()
        worklist_origin = WorkInfo.objects.all()
        # work = WorkInfo.objects.get(work_id='1').wo
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
                'work_id': work.work_id,
                'first_author': work.registration.first_auth.name,
                'title': work.title,
                'work_type': WORKTYPE_MAP[work.work_type],
                'field': FIELD_MAP[work.field],
                'competition': work.registration.competition.title,
                'submitted': "已提交" if work.submitted else "暂存",
            })

        user_name, user_identity = GetUserIdentitiy(request)
        return render(request, 'reviewwork_list.html', {'worklist': worklist_ret,'useridentity':user_identity})

