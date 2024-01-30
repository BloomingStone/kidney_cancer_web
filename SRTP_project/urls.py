from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path(r'admin/', admin.site.urls),
    path(r'login/', views.login, name='login'),
    path(r'logout/',views.logout, name='logout'),
    path(r'index/', views.index, name='index'),
    path(r'build/<int:image_id>', views.build, name='build'),
    path(r'report/<int:report_id>', views.report_alter, name='report_alter'),
    path(r'report/new/',views.report_new, name='report_new'),
    path(r'', views.home),
    path(r'gz/<str:filename>', views.gz_compression_response),
    path(r'build/seg', views.segmentation),
    path(r'build/save/<str:filename>', views.save_picture),
    # path('build/StreamingAssets/<str:filename>', views.streaming),
    path(r'image-report/', views.image_report)
]
