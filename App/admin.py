from django.contrib import admin
from App import models


# Register your models here.
admin.site.register(models.Doctor)
admin.site.register(models.Patient)
admin.site.register(models.Image)
admin.site.register(models.Report)
admin.site.register(models.ImageReport)
