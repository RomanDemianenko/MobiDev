"""mobidev URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views
from rest_framework import routers

from service.api.resourse import AuthToken, EmployeeViewSet, CompanyViewSet, ProfileViewSet, OfficeViewSet, \
    DetailOfficeViewSet, EmployeeUpViewsSet, AssignEmployeeToOfficeViewSet, EmployeeOfficeDetailViewSet, VehicleViewSet, \
    VehicleChangeViewSet, VehicleProfileViewSet, CompanyCreateViewSet


router = routers.SimpleRouter()
router.register(r'auth', CompanyCreateViewSet, basename='auth')
router.register(r'employee', EmployeeViewSet, basename='employee')
router.register(r'employee_up', EmployeeUpViewsSet, basename='employee_up')
router.register(r'company', CompanyViewSet, basename='company')
router.register(r'profile', ProfileViewSet, basename='profile')
router.register(r'office', OfficeViewSet, basename='office')
router.register(r'detail_office', DetailOfficeViewSet, basename='office')
router.register(r'employee_office', AssignEmployeeToOfficeViewSet, basename='employee_office')
router.register(r'employee_office_detail', EmployeeOfficeDetailViewSet, basename='employee_office_detail')
router.register(r'vehicle', VehicleViewSet, basename='vehicle')
router.register(r'vehicle_change', VehicleChangeViewSet, basename='vehicle_change')
router.register(r'vehicle_profile', VehicleProfileViewSet, basename='vehicle_profile')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path('api-token-auth/', AuthToken.as_view()),
    path('admin/', admin.site.urls),
]
