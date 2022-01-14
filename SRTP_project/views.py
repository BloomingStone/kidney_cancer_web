from django.shortcuts import render
from App.models import User
from App.models import Patient
from django.http import HttpResponseRedirect


def login(request):
    if request.method == 'POST' and request.POST:
        username = request.POST.get("username")
        password = request.POST.get("password")
        require = User.objects.filter(username=username).first()  # 取出第一个username和输入相等的第一个查询结果
        if require:
            if password == require.password:
                response = HttpResponseRedirect('/index/')
                # response.set_cookie("username", require.username)
                return response

    return render(request, "login.html")


def index(request):
    image_path = None
    if request.method == 'POST' and request.POST:
        patient_id = request.POST.get("patient_id")
        require = Patient.objects.filter(patient_id=patient_id).first()  # 别忘加first
        if require:
            # 以下是测试, 实际上我们要能打开路径对应的3d图像
            image_path = require.image_path
    context = {
        'path': image_path
    }
    return render(request, "index.html", context)
