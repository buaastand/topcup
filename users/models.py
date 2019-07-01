from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class BaseUser(AbstractUser):
    USER_TYPE = (
        (1, "sturdent"),
        (2, "admin"),
        (3, "expert")
    )
    type = models.IntegerField(choices=USER_TYPE, verbose_name="用户类型")

    class Meta:
        verbose_name = "基础用户"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


class Student(models.Model):
    DEGREE_TYPE = (
        (1, "大专"),
        (2, "大学本科"),
        (3, "硕士研究生"),
        (4, "博士研究生"),
    )
    user = models.OneToOneField(BaseUser, on_delete=models.CASCADE, primary_key=True)
    stu_id = models.CharField(max_length=255, unique=True, verbose_name="学号")
    name = models.CharField(max_length=255, verbose_name="姓名")
    department = models.CharField(max_length=255, verbose_name="院系")
    major = models.CharField(max_length=255, verbose_name="专业")
    enroll_time = models.DateField(verbose_name="入学年份")
    phone = models.CharField(max_length=255, verbose_name="联系电话")
    birthdate = models.DateField(verbose_name="出生日期")
    degree = models.IntegerField(choices=DEGREE_TYPE, verbose_name="学历")
    address = models.CharField(max_length=255, verbose_name="通信地址")

    class Meta:
        verbose_name = "学生用户"
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.stu_id) + "-" + str(self.name)


class Expert(models.Model):
    FIELD_TYPE = (
        (1, "A"),
        (2, "B"),
        (3, "C"),
        (4, "D"),
        (5, "E"),
        (6, "F"),
    )
    user = models.OneToOneField(BaseUser, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=255, verbose_name="姓名")
    field = models.IntegerField(choices=FIELD_TYPE, verbose_name="专业领域")
    activated = models.BooleanField(null=False, default=False, verbose_name="是否激活")

    class Meta:
        verbose_name = "专家用户"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
