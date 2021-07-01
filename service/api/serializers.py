from django.contrib.auth import authenticate
from rest_framework import serializers

from service.models import MyUser, Company, Office, Vehicle


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ('id', 'company_name')


class UserRegisterSerializer(serializers.ModelSerializer):
    """Serializer for Create Company, where user automatically become the Admin of Company.
    We use nested CompanySerializer and take field company_name.  """
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


class EmployeeCreateSerializer(serializers.ModelSerializer):
    """Admin can create Employee for his company."""
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
    """Employee can see his profile, and change it, exclude EMAIL"""
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
        fields = ('id', 'office_name', 'address', 'country', 'city', 'region', 'employee')
        read_only_fields = ('id', 'employee')


class AssignEmployeeToOfficeSerializer(serializers.ModelSerializer):
    """Employee can be only assigned to a one office"""
    class Meta:
        model = Office
        fields = ('id', 'employee')

    def validate(self, data):
        employee = data['employee']
        if Office.objects.filter(employee=employee).exists():
            raise serializers.ValidationError(f'This {employee} has already exists in a current office')
        return data


class VehicleSerializer(serializers.ModelSerializer):
    """Serializer for create Vehicle. Driver should belong to the office chosen by admin. """
    class Meta:
        model = Vehicle
        fields = ('id', 'licence_plate', 'name', 'model', 'year_of_manufacture', 'office', 'driver')

        extra_kwargs = {
            'driver': {'required': False, "allow_null": True, "default": None},
            'office': {'required': False, "allow_null": True, "default": None}
        }

    def validate(self, data):
        if data['driver'] is not None and data['office'] is not None:
            if Office.objects.filter(employee=data['driver']).filter(id=data['office'].id):
                pass
            else:
                raise serializers.ValidationError(f'The Employee work in another office')
            return data
        else:
            return data
