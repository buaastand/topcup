from django.db import models
from users.models import Student


# Create your models here.
class Competition(models.Model):
    COMPETITION_STATUS_TYPE = (
        (0, "未开始"),
        (1, "报名阶段"),
        (2, "初审阶段"),
        (3, "初评阶段"),
        (4, "现场答辩阶段"),
        (5, "已结束")
    )
    title = models.CharField(max_length=255, verbose_name="竞赛标题")
    abstract = models.TextField(verbose_name="竞赛摘要")
    detail = models.TextField(verbose_name="竞赛详细信息")
    rule = models.TextField(verbose_name="竞赛规则")
    status = models.IntegerField(choices=COMPETITION_STATUS_TYPE, verbose_name="竞赛状态")
    init_date = models.DateField(verbose_name="竞赛开始时间")
    submit_end_date = models.DateField(verbose_name="提交截止时间")
    check_end_date = models.DateField(verbose_name="初审截止时间")
    review_end_date = models.DateField(verbose_name="初评截止时间")
    defense_end_date = models.DateField(verbose_name="现场答辩结束时间")
    finish_date = models.DateField(verbose_name="竞赛终止时间")
    preview_img = models.ImageField(upload_to="competition/img/", verbose_name="预览图")
    detail_img = models.ImageField(upload_to="competition/img/", verbose_name="详情图")
    result_details = models.TextField(verbose_name="比赛结果详情")
    start_appendix = models.FileField(upload_to="competition/appendix/", verbose_name="比赛公告附件")
    end_appendix = models.FileField(upload_to="competition/appendix/", verbose_name="比赛结果附件")

    class Meta:
        verbose_name = "科技竞赛"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class CompetitionRegistration(models.Model):
    first_auth = models.ForeignKey(Student, null=True, on_delete=models.CASCADE, verbose_name="第一作者", related_name="+")
    second_auth = models.ForeignKey(Student, null=True, on_delete=models.CASCADE, verbose_name="第二作者", related_name="+")
    third_auth = models.ForeignKey(Student, null=True, on_delete=models.CASCADE, verbose_name="第三作者", related_name="+")
    forth_auth = models.ForeignKey(Student, null=True, on_delete=models.CASCADE, verbose_name="第四作者", related_name="+")
    fifth_auth = models.ForeignKey(Student, null=True, on_delete=models.CASCADE, verbose_name="第五作者", related_name="+")
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, verbose_name="竞赛")

    class Meta:
        verbose_name = "竞赛注册"
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.first_auth) + ':' + str(self.competition)
