from django.contrib import admin
from App import models


# Register your models here.
admin.site.register(models.User)
admin.site.register(models.Patient)
