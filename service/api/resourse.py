from django.contrib.auth.hashers import make_password
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, permissions
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import get_object_or_404
from service.api.serializers import MyAuthTokenSerializer, WorkerCreateSerializer, \
    CompaniesSerializer, ProfileSerializer, OfficeSerializer, OfficeDetailSerializer, AddWorkerToOfficeSerializer, \
    VehicleSerializer, UserRegisterSerializer
from service.models import MyUser, Company, Office, Vehicle
from rest_framework.authtoken.models import Token


class CompanyCreateViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny, ]
    serializer_class = UserRegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data['password'] != serializer.validated_data['confirm_password']:
            data = {"Passwords don`t pass"}
            return Response(data=data, status=status.HTTP_409_CONFLICT)
        if serializer.is_valid():
            company = serializer.validated_data['company']
            company_name = company['company_name']
            company_obj = Company.objects.create(company_name=company_name)
            serializer.validated_data['company'] = company_obj
            serializer.validated_data.pop('confirm_password')
            user = MyUser.objects.create(is_staff=True, **serializer.validated_data)
            user.set_password(serializer.validated_data['password'])
            user.save()
            company_obj.save()
            data = {'success': 'You create the company Successfully'}
            return Response(data=data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthToken(ObtainAuthToken):
    """Create token by Email"""
    serializer_class = MyAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token = Token.objects.get_or_create(user=user)

            return Response({'token': token[0].key, 'email': user.email})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WorkerViewSet(viewsets.ModelViewSet):
    """Admin can create a worker of his company(without field admin), can see list of company workers
    and filter them by first name, last name, email"""
    permission_classes = [IsAdminUser, ]
    serializer_class = WorkerCreateSerializer
    queryset = MyUser.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['first_name', 'last_name', 'email']

    def create(self, request, *args, **kwargs):
        serializer = WorkerCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data['password'] != serializer.validated_data['confirm_password']:
            data = {"Passwords don`t pass"}
            return Response(data=data, status=status.HTTP_409_CONFLICT)
        if serializer.is_valid():
            company = self.request.user.company
            serializer.validated_data.pop('confirm_password')
            user = MyUser.objects.create(company=company, **serializer.validated_data)
            user.set_password(serializer.validated_data['password'])
            user.save()
            company.save()
            data = {'success': 'You add worker to company'}
            return Response(data=data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        queryset = MyUser.objects.filter(company=self.request.user.company, is_staff=False)
        return queryset


class WorkerUpViewsSet(viewsets.ModelViewSet):
    """Admin can change(first name, last name, password, NOT email), see details(first name, last name, email)
    and delete worker"""
    permission_classes = [IsAdminUser, ]
    serializer_class = ProfileSerializer
    queryset = MyUser.objects.all()

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        queryset = MyUser.objects.filter(id=pk, company=self.request.user.company, is_staff=False)

        return queryset

    def put(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        company = self.request.user.company
        worker = get_object_or_404(MyUser.objects.filter(pk=pk, company=company, is_staff=False))
        serializer = ProfileSerializer(instance=worker, data=request.data, partial=True)

        if serializer.is_valid():
            self.perform_update(serializer)
            serializer.save()
            return Response(serializer.errors, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        pk = self.kwargs.get('pk')
        office = get_object_or_404(MyUser.objects.filter(id=pk, company=self.request.user.company))
        office.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_update(self, serializer):
        hashed_password = make_password(serializer.validated_data['password'])
        serializer.validated_data['password'] = hashed_password
        worker = super(WorkerUpViewsSet, self).perform_update(serializer)
        return worker


class CompanyViewSet(viewsets.ModelViewSet):
    """Like worker or admin you can see info about your company, admin can change his name and address"""
    serializer_class = CompaniesSerializer
    queryset = Company.objects.all()

    def get_queryset(self):
        queryset = Company.objects.filter(id=self.request.user.company.id)
        return queryset

    def put(self, request, *args, **kwargs):
        pk = self.request.user.company.id
        company = get_object_or_404(Company.objects.filter(id=pk))
        serializer = CompaniesSerializer(instance=company, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.errors, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        elif self.request.method == 'PUT':
            return [permissions.IsAdminUser()]


class ProfileViewSet(viewsets.ModelViewSet):
    """Like a worker of company, You can see your profile(first name, last name, email) and change the password"""
    serializer_class = ProfileSerializer
    queryset = MyUser.objects.all()

    def get_queryset(self):
        queryset = MyUser.objects.filter(id=self.request.user.id)
        return queryset

    def put(self, request, *args, **kwargs):
        pk = self.request.user.id
        user = get_object_or_404(MyUser.objects.filter(id=pk))
        serializer = ProfileSerializer(instance=user, data=request.data, partial=True)

        if serializer.is_valid():
            user.set_password(serializer.validated_data.get('password'))
            user.save()
            return Response(serializer.errors, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OfficeViewSet(viewsets.ModelViewSet):
    """Admin can create the office, and admin and worker can see list of company offices"""
    serializer_class = OfficeSerializer
    queryset = Office.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['country', 'city']

    def create(self, request, *args, **kwargs):
        serializer = OfficeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.is_valid():
            company = self.request.user.company
            office = Office.objects.create(company=company, **serializer.validated_data)
            office.save()
            data = {'success': 'You create the company Successfully'}
            return Response(data=data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        queryset = Office.objects.filter(company=self.request.user.company)

        return queryset

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        elif self.request.method == 'POST':
            return [permissions.IsAdminUser()]


class DetailOfficeViewSet(viewsets.ModelViewSet):
    """Admin can change/delete/see details one of his offices"""
    permission_classes = [IsAdminUser, ]
    serializer_class = OfficeDetailSerializer
    queryset = Office.objects.all()

    def put(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        office = get_object_or_404(Office.objects.filter(id=pk, company=self.request.user.company))
        serializer = OfficeDetailSerializer(instance=office, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.errors, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        pk = self.kwargs.get('pk')
        office = get_object_or_404(Office.objects.filter(id=pk, company=self.request.user.company))
        office.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        queryset = Office.objects.filter(id=pk, company=self.request.user.company)

        return queryset


class WorkerOfficeViewSet(viewsets.ModelViewSet):
    """Admin can appoint to one of companies offices"""
    permission_classes = [IsAdminUser, ]
    serializer_class = AddWorkerToOfficeSerializer
    queryset = Office.objects.all()

    def put(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        office = get_object_or_404(Office.objects.filter(id=pk, company=self.request.user.company))
        serializer = AddWorkerToOfficeSerializer(instance=office, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.errors, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        queryset = Office.objects.filter(company=self.request.user.company)
        return queryset


class WorkerOfficeDetailViewSet(viewsets.ModelViewSet):
    """Worker cas see details his office"""
    serializer_class = OfficeDetailSerializer
    queryset = Office.objects.all()

    def get_queryset(self):
        queryset = Office.objects.filter(worker=self.request.user.id)
        return queryset


class VehicleViewSet(viewsets.ModelViewSet):
    """Admin can create vehicle and add optinal office and driver"""
    permission_classes = [IsAdminUser, ]
    serializer_class = VehicleSerializer
    queryset = Vehicle.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['driver', 'office']

    def create(self, request, *args, **kwargs):
        serializer = VehicleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.is_valid():
            company = self.request.user.company
            vehicle = Vehicle.objects.create(company=company, **serializer.validated_data)
            vehicle.save()
            data = {'success': 'You create the Vehicle Successfully'}
            return Response(data=data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        queryset = Vehicle.objects.filter(company=self.request.user.company)

        return queryset


class VehicleChangeViewSet(viewsets.ModelViewSet):
    """Admin can delete/change/get a details vehicle """
    permission_classes = [IsAdminUser, ]
    serializer_class = VehicleSerializer
    queryset = Vehicle.objects.all()

    def put(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        vehicle = get_object_or_404(Vehicle.objects.filter(id=pk, company=self.request.user.company))
        serializer = OfficeDetailSerializer(instance=vehicle, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.errors, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        pk = self.kwargs.get('pk')
        vehicle = get_object_or_404(Vehicle.objects.filter(id=pk, company=self.request.user.company))
        vehicle.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        queryset = Vehicle.objects.filter(id=pk, company=self.request.user.company)

        return queryset


class VehicleProfileViewSet(viewsets.ModelViewSet):
    """You can see a list of vehicles whose driver you are"""
    serializer_class = VehicleSerializer
    queryset = Vehicle.objects.all()

    def get_queryset(self):
        driver = self.request.user.id
        queryset = Vehicle.objects.filter(driver=driver)
        return queryset
