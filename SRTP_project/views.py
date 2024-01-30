import os
import tempfile
from shutil import copyfile
from django.shortcuts import render
from App.models import Doctor, Patient, Image, Report, ImageReport
from django.core import exceptions
from django.http import HttpResponseRedirect, HttpResponse, Http404, StreamingHttpResponse, FileResponse, JsonResponse
from _3DUNetKidney.Predict import predict
from django.views.decorators.csrf import csrf_exempt


def check_login(func):
    # 编写装饰器检测用户是否登录
    def inner(request, *args, **kwargs):
        if request.session.get('is_login'):
            # 如果已经登录
            return func(request, *args, **kwargs)
        else:
            return HttpResponseRedirect('/login/')
    return inner


def login(request):
    if request.session.get('is_login'):
        return HttpResponseRedirect('/index/')

    if request.method == 'POST' and request.POST:
        username = request.POST.get("username")
        password = request.POST.get("password")
        require = Doctor.objects.filter(username=username).first()  # 取出第一个username和输入相等的第一个查询结果
        # print(require)
        if require:
            if password == require.password:
                response = HttpResponseRedirect('/index/')
                request.session['is_login'] = True
                request.session['doctor_id'] = require.id
                return response
            else:
                return render(request, "login.html", {"error_message": "用户名或密码错误"})

    return render(request, "login.html")


def logout(request):
    rep = HttpResponseRedirect("/")
    # request.session.delete()
    # 登出，则删除掉session中的某条数据
    if 'is_login' in request.session:
        del request.session['is_login']
        request.session.clear()
    return rep


@check_login
def index(request):
    ctx = {}
    try:
        patient_id = request.session["temp"]

        patient_get = Patient.objects.get(patient_id=patient_id)
        patient_accessible = Patient.objects.filter(doctor__id=request.session['doctor_id'])
        assert patient_get in patient_accessible  # 判断是否有权访问该病人信息
        image_list = patient_get.image_set.order_by('-time')
        report_list = patient_get.report_set.order_by('-time')

        ctx = {
            "image_list": image_list,
            "report_list": report_list
        }
    except:
        print('bug')

    try:
        if request.method == 'POST' and request.POST:
            patient_id = request.POST.get("patient_id")

            patient_get = Patient.objects.get(patient_id=patient_id)
            patient_accessible = Patient.objects.filter(doctor__id=request.session['doctor_id'])
            assert patient_get in patient_accessible    # 判断是否有权访问该病人信息
            image_list = patient_get.image_set.order_by('-time')
            report_list = patient_get.report_set.order_by('-time')

            request.session['patient_id'] = patient_get.id  # 储存选中的信息
            request.session['temp'] = patient_id
            print(request.session['patient_id'])

            ctx = {
                "image_list": image_list,
                "report_list": report_list
            }

    except AssertionError:
        ctx = {'error_message': '你无权访问该病人信息'}
    except ValueError:
        ctx = {'error_message': '输入错误'}
    except exceptions.ObjectDoesNotExist:
        ctx = {"error_message": "病人不存在"}

    print(ctx)
    return render(request, "index.html", ctx)


@check_login
def build(request, image_id):
    image = Image.objects.get(id=image_id)
    request.session["image_id"] = image_id
    path = '.'+image.path
    request.session['image_path'] = path
    patient = Patient.objects.get(id=request.session['patient_id'])
    ctx = {
        "patient": patient,
        "gender": patient.get_gender_display(),
        'image_time': image.time,
        "image_report": ""
    }
    if hasattr(image, 'imagereport'):
        ctx["image_report"] = image.imagereport
    if os.path.exists(path):
        copyfile(path, "./static/build/StreamingAssets/data.raw")

    return render(request, "build.html", ctx)


@csrf_exempt
def image_report(request):
    image = Image.objects.get(id=request.session['image_id'])
    patient = Patient.objects.get(id=request.session['patient_id'])
    ctx = {
        "image": image,
        "patient": patient,
        "image_report": ""
    }

    if hasattr(image, 'imagereport'):
        ctx["image_report"] = image.imagereport

    if request.method == 'POST' and request.POST:
        observation = request.POST.get("observation")
        impression = request.POST.get("impression")

        if hasattr(image, 'imagereport'):
            image.imagereport.observation = observation
            image.imagereport.impression = impression
            doctor = Doctor.objects.get(id=request.session['doctor_id'])
            image.imagereport.doctor = doctor
            image.imagereport.save()

        else:
            doctor = Doctor.objects.get(id=request.session['doctor_id'])
            r = ImageReport.objects.create(
                observation=observation,
                impression=impression,
                image=image,
                doctor=doctor
            )
            r.save()

        return JsonResponse({'status': 200, 'message': 'add event success'})


def segmentation(request):
    path = request.session.get('image_path')
    id = request.session.get('image_id')
    print(path)
    temp_path = os.path.join('./temporary/image/', str(id))
    print(temp_path)
    if os.path.exists(temp_path):   # 若临时文件中存在对应图像文件，将临时文件中的分割结果复制到
        copyfile(temp_path, "./static/build/StreamingAssets/tag.raw")
    else:
        if os.path.exists(path):
            predict(path, "./static/build/StreamingAssets/tag.raw")
            copyfile("./static/build/StreamingAssets/tag.raw", temp_path)

    response = HttpResponse()
    response.content = "get"
    return response


@check_login
def report_alter(request, report_id):
    # 同上, 这里也应该修改
    report = Report.objects.get(id=report_id)
    # if report:
    #     print("success")
    #     print(report)
    #     print("success")
    # else:
    #     print("unsuc")
    if request.method == 'POST' and request.POST:
        if 'alter' in request.POST:
            report.name = request.POST.get("name")
            report.analyse = request.POST.get("analyse")
            report.conclusion = request.POST.get("conclusion")
            print(report.conclusion)
            report.save()
            return HttpResponseRedirect('/index/')
        if 'delete' in request.POST:
            report.delete()
            return HttpResponseRedirect('/index/')
    return render(request, "report.html", {"report": report})


@check_login
def report_new(request):
    patient = Patient.objects.get(id=request.session['patient_id'])
    doctor = Doctor.objects.get(id=request.session['doctor_id'])
    ctx = {
        "patient_name": patient.name,
        "doctor_name": doctor.name
    }
    if request.method == 'POST' and request.POST:

        name = request.POST.get("name")
        analyse = request.POST.get("analyse")
        conclusion = request.POST.get("conclusion")
        Report.objects.create(
            name=name,
            analyse=analyse,
            conclusion=conclusion,
            patient=patient,
            doctor=doctor
        )
        HttpResponseRedirect('/index/')
    return render(request, 'report_new.html', ctx)


def home(request):
    return render(request, 'home.html')


def gz_compression_response(request, filename):
    with open('./gz/{}'.format(filename), 'rb') as f:
        js_content = f.read()
    response = HttpResponse()
    response.content = js_content
    if 'js' in filename:
        response['Content-Type'] = 'application/javascript'
    elif 'wasm' in filename:
        response['Content-Type'] = 'application/wasm'
    else:
        pass
    response['Content-Encoding'] = 'gzip'
    return response


@csrf_exempt
def save_picture(request, filename):
    pic = request.body
    temp_file_path = './temporary/temp.png'
    try:
        with open(temp_file_path, 'wb') as t:
            t.write(pic)
        response = FileResponse(open(temp_file_path, 'rb'))
        response['Content-Type'] = "application/octet-stream"
        response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(filename)
        response['Content-Length'] = os.path.getsize(temp_file_path)
        return response

    except Exception:
        raise Http404


def streaming(request, filename):
    if filename == 'tag.raw':
        path = request.session.get('image_path')
        if os.path.exists(path):
            predict(path, "./StreamingAssets/tag.raw")

    with open('./StreamingAssets/{}'.format(filename), 'rb') as f:
        raw_content = f.read()
    response = HttpResponse()
    response.content = raw_content
    return response
