from django.contrib import admin

# Register your models here.
from service.models import MyUser, Company, Office, Vehicle

admin.site.register(MyUser)
admin.site.register(Company)
admin.site.register(Office)
admin.site.register(Vehicle)