from django.db import models
from django.contrib.auth.models import User


class Doctor(models.Model):
    username = models.CharField(max_length=32)  # 用户名
    password = models.CharField(max_length=32)  # 密码
    name = models.CharField(max_length=32, default="None")  # 姓名

    def __str__(self):
        return self.name
    # Django 规定，如果要使用模型，必须要创建一个 app。
    # 同时要在setting的INSTALLED_APPS中添加对应app
    # 此处创建了一个名为user的表,表中有两项: username和password
    # 关于权限设置, 现准备考虑采用多对多表进行管理, 但Django自带有auth模块
    # 也许可以用来设置权限.


class Patient(models.Model):
    SEX_CHOICES = (
        (0, ''),
        (1, '男'),
        (2, '女'),
    )
    patient_id = models.IntegerField()  # 病人id
    name = models.CharField(max_length=32, default="None")  # 姓名
    gender = models.IntegerField(choices=SEX_CHOICES, default=0)  # 性别
    age = models.IntegerField(default=0)  # 年龄
    department = models.CharField(max_length=32, default='None')  # 所属科室
    doctor = models.ManyToManyField(Doctor)     # 治疗医生

    def __str__(self):
        return self.name


class Image(models.Model):
    name = models.CharField(max_length=32,default="None")   # 图像名
    path = models.CharField(max_length=64)  # 存放图片路径
    patient = models.ForeignKey("Patient", on_delete=models.CASCADE)  # 外键关联到patient,下面类似
    time = models.DateTimeField(auto_now_add=True)  # 检查图像时期

    def __str__(self):
        return self.name


class Report(models.Model):
    """
    诊断报告
    """
    name = models.CharField(max_length=50)  # 报告名
    time = models.DateTimeField(auto_now=True)  # 保存最后修改时间
    analyse = models.TextField(blank=True)  # 分析
    conclusion = models.TextField(blank=True)   # 结论
    patient = models.ForeignKey("Patient", on_delete=models.CASCADE,)   # 对应的病人
    doctor = models.ForeignKey("Doctor", on_delete=models.CASCADE)  # 对应的医生

    def __str__(self):
        return self.name


class ImageReport(models.Model):
    """
    图像诊断报告
    """
    observation = models.TextField(blank=True)  # 影像所见
    impression = models.TextField(blank=True)   # 印象
    time = models.DateTimeField(auto_now=True)  # 保存最后修改时间

    image = models.OneToOneField("Image", on_delete=models.CASCADE)
    # image = models.ForeignKey("Image", on_delete=models.CASCADE)    # 报告对应的图像
    doctor = models.ForeignKey("Doctor", on_delete=models.CASCADE)  # 报告对应的医生


