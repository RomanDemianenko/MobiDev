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

from service.api.resourse import AuthToken, AuthViewSet, WorkerViewSet, CompanyViewSet, ProfileViewSet, OfficeViewSet, \
    DetailOfficeViewSet, WorkerUpViewsSet, WorkerOfficeViewSet, WorkerOfficeDetailViewSet, VehicleViewSet, \
    VehicleChangeViewSet, VehicleProfileViewSet
from service.views import CompanyRegistrationView, UserLogout, ServiceList, WorkerCreate, WorkerList, WorkerDetail, \
    WorkerUpdate, WorkerDelete, CompanyDetail, CompanyUpdate, ProfileUpdate, OfficeCreate, OfficeList, OfficeDetail, \
    OfficeUpdate, OfficeDelete, AddWorkerToOfficeUpdate, WorkerOfficeList, VehicleCreate, VehicleList, \
    AddWorkerToVehicleUpdate, VehicleUpdate, VehicleDelete, MyVehicleList

router = routers.SimpleRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'worker', WorkerViewSet, basename='worker')
router.register(r'worker_up', WorkerUpViewsSet, basename='worker_up')
router.register(r'company', CompanyViewSet, basename='company')
router.register(r'profile', ProfileViewSet, basename='profile')
router.register(r'office', OfficeViewSet, basename='office')
router.register(r'detail_office', DetailOfficeViewSet, basename='office')
router.register(r'worker_office', WorkerOfficeViewSet, basename='worker_office')
router.register(r'worker_office_detail', WorkerOfficeDetailViewSet, basename='worker_office_detail')
router.register(r'vehicle', VehicleViewSet, basename='vehicle')
router.register(r'vehicle_change', VehicleChangeViewSet, basename='vehicle_change')
router.register(r'vehicle_profile', VehicleProfileViewSet, basename='vehicle_profile')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path('api-token-auth/', AuthToken.as_view()),
    path('admin/', admin.site.urls),
    path('service/', ServiceList.as_view(), name='service'),
    path('company-regist/', CompanyRegistrationView.as_view(), name='register_company'),
    path('login/', views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', UserLogout.as_view(), name='logout'),
    path('worker_create/', WorkerCreate.as_view(), name='worker_create'),
    path('worker_list/', WorkerList.as_view(), name='worker_list'),
    path('worker_detail/<int:pk>/', WorkerDetail.as_view(), name='worker_detail'),
    path('worker_update/<int:pk>/', WorkerUpdate.as_view(), name='worker_update'),
    path('worker_delete/<int:pk>/', WorkerDelete.as_view(), name='worker_delete'),
    path('company_detail/<int:pk>/', CompanyDetail.as_view(), name='company_detail'),
    path('company_update/<int:pk>/', CompanyUpdate.as_view(), name='company_update'),
    path('profile_update/<int:pk>/', ProfileUpdate.as_view(), name='profile_update'),
    path('office_create', OfficeCreate.as_view(), name='office_create'),
    path('office_list/', OfficeList.as_view(), name='office_list'),
    path('office_detail/<int:pk>/', OfficeDetail.as_view(), name='office_detail'),
    path('office_update/<int:pk>/', OfficeUpdate.as_view(), name='office_update'),
    path('office_delete/<int:pk>/', OfficeDelete.as_view(), name='office_delete'),
    path('add_worker_to_office/<int:pk>/', AddWorkerToOfficeUpdate.as_view(), name='add_worker'),
    path('worker_office_detail/', WorkerOfficeList.as_view(), name='worker_office'),
    path('vehicle_create/', VehicleCreate.as_view(), name='vehicle_create'),
    path('vehicle_list/', VehicleList.as_view(), name='vehicle_list'),
    path('add_worker_vehicle/<int:pk>/', AddWorkerToVehicleUpdate.as_view(), name='worker_vehicle'),
    path('vehicle_update/<int:pk>/', VehicleUpdate.as_view(), name='vehicle_update'),
    path('vehicle_delete/<int:pk>/', VehicleDelete.as_view(), name='vehicle_delete'),
    path('yourself_vehicle_list', MyVehicleList.as_view(), name='yourself_vehicle_list')
]
