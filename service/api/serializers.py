from django.contrib.auth import authenticate
from rest_framework import serializers

from service.models import MyUser, Company, Office, Vehicle


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ('id', 'company_name')


class UserRegisterSerializer(serializers.ModelSerializer):
    """Serializer for Create Company, where user automatically become the Admin of Company.
    We use nested Companyserializer and take filed company_name.  """
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    email = serializers.EmailField(label="email", required=True)
    company = CompanySerializer()

    class Meta:
        model = MyUser
        fields = ('id', 'first_name', 'last_name', 'email', 'password', 'confirm_password', 'company')

    def validate(self, data):
        email = data['email']
        if MyUser.objects.filter(email=email).exists():
            raise serializers.ValidationError(f'This {email} has already registration')
        return data


class MyAuthTokenSerializer(serializers.Serializer):
    """We can get Token by email """
    email = serializers.EmailField(label="Email", required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)

            if not user:
                error = ("Wrong email or password")
                raise serializers.ValidationError(error)

        else:
            error = ("You should fill fields")
            raise serializers.ValidationError(error)
        attrs['user'] = user

        return attrs


class WorkerCreateSerializer(serializers.ModelSerializer):
    """Admin can create worker for his company."""
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    email = serializers.EmailField(label="Email", required=True)

    class Meta:
        model = MyUser
        fields = ('id', 'first_name', 'last_name', 'email', 'password', 'confirm_password')

    def validate(self, data):
        email = data['email']
        if MyUser.objects.filter(email=email).exists():
            raise serializers.ValidationError(f'This {email} has already registration')
        return data


class CompaniesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ('id', 'company_name', 'address')


class ProfileSerializer(serializers.ModelSerializer):
    """Worker can see his profile, and change it, exclude EMAIL"""
    class Meta:
        model = MyUser
        fields = ('id', 'first_name', 'last_name', 'email', 'password')
        read_only_fields = ('id', 'email')
        extra_kwargs = {
            'password': {'write_only': True},
        }


class OfficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Office
        fields = ('id', 'office_name', 'address', 'country', 'city', 'region')


class OfficeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Office
        fields = ('id', 'office_name', 'address', 'country', 'city', 'region', 'worker')
        read_only_fields = ('id', 'worker')


class AssignWorkerToOfficeSerializer(serializers.ModelSerializer):
    """We assign worker to office, and he can be only in one office"""
    class Meta:
        model = Office
        fields = ('id', 'worker')

    def validate(self, data):
        worker = data['worker']
        if Office.objects.filter(worker=worker).exists():
            raise serializers.ValidationError(f'This {worker} has already working in office')
        return data


class VehicleSerializer(serializers.ModelSerializer):
    """Serializer for create Vehicle. When admin choose driver and office for vehicle,
     driver must work in the same office, which choose Admin. """
    class Meta:
        model = Vehicle
        fields = ('id', 'licence_plate', 'name', 'model', 'year_of_manufacture', 'office', 'driver')

        extra_kwargs = {
            'driver': {'required': False, "allow_null": True, "default": None},
            'office': {'required': False, "allow_null": True, "default": None}
        }

    def validate(self, data):
        if data['driver'] is not None and data['office'] is not None:
            if Office.objects.filter(worker=data['driver']).filter(id=data['office'].id):
                pass
            else:
                raise serializers.ValidationError(f'The Worker work in another office')
            return data
        else:
            return data
