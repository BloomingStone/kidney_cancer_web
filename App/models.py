from django.db import models


class User(models.Model):
    username = models.CharField(max_length=32)
    password = models.CharField(max_length=32)
    # Django 规定，如果要使用模型，必须要创建一个 app。
    # 同时要在setting的INSTALLED_APPS中添加对应app
    # 此处创建了一个名为user的表,表中有两项: username和password


class Patient(models.Model):
    """
    病人信息表, 此处只存放图像路径, 经有路径在对应地址打开
    """
    patient_id = models.IntegerField()
    image_path = models.CharField(max_length=64)
