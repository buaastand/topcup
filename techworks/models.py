from django.db import models

from competition.models import CompetitionRegistration


# Create your models here.
class WorkInfo(models.Model):
    WORK_TYPE = (
        (1, "科技发明制作"),
        (2, "调查报告和学术论文")
    )
    FIELD_TYPE = (
        (1, "A"),
        (2, "B"),
        (3, "C"),
        (4, "D"),
        (5, "E"),
        (6, "F"),
    )
    work_id = models.IntegerField(verbose_name="作品编号")
    work_type = models.IntegerField(choices=WORK_TYPE, verbose_name="大类类别")
    title = models.CharField(max_length=255, verbose_name="作品名称")
    department = models.CharField(max_length=255, verbose_name="院系名称")
    field = models.IntegerField(choices=FIELD_TYPE, verbose_name="专业领域")
    registration = models.ForeignKey(CompetitionRegistration, on_delete=models.CASCADE, verbose_name="参赛记录")
    detail = models.TextField(verbose_name="作品总体情况说明")
    innovation = models.TextField(verbose_name="创新点")
    keywords = models.CharField(max_length=255, verbose_name="关键词")
    check_status = models.BooleanField(default=False, verbose_name="初审结果")
    avg_score = models.FloatField(verbose_name="平均分")
    if_defense = models.BooleanField(default=False, verbose_name="是否答辩")
    submitted = models.BooleanField(default=False,verbose_name="是否已提交")
    labels = models.CharField(max_length=255, verbose_name="作品标签", default="{\"labels\":[]}")

    class Meta:
        verbose_name = "作品"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class Appendix(models.Model):
    APPENDIX_TYPE = (
        (1, "文档"),
        (2, "图片"),
        (3, "视频")
    )
    filename = models.CharField(max_length=255, verbose_name="文件名")
    appendix_type = models.IntegerField(choices=APPENDIX_TYPE, verbose_name="文件类型")
    work = models.ForeignKey(WorkInfo, on_delete=models.CASCADE, verbose_name="作品")
    upload_date = models.DateField(verbose_name="上传日期")
    file = models.FileField(upload_to="techwork/", verbose_name="文件")

    class Meta:
        verbose_name = "附件"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.filename
