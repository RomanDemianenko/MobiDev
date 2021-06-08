from django.contrib.auth import authenticate
from rest_framework import serializers

from service.models import MyUser, Company, Office, Vehicle


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ('id', 'company_name')


class CreateCompanySerializer(serializers.ModelSerializer):
    """User can create profile and company, and user get admin role in this company"""
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    email = serializers.EmailField(label="email", required=True)
    company = CompanySerializer()

    class Meta:
        model = MyUser
        fields = ('id', 'first_name', 'last_name', 'email', 'password', 'confirm_password', 'company')

    def create(self, validated_data):
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        email = validated_data['email']
        password = validated_data.pop('password')
        company = validated_data['company']
        company_name = company['company_name']
        company_obj = Company.objects.create(company_name=company_name)
        # validated_data['company'] = company
        # company_obj.company_name.set(company_name)

        user = MyUser.objects.create(first_name=first_name, last_name=last_name, email=email, password=password,
                                     company=company_obj, is_staff=True)
        user.set_password(password)
        user.save()
        company_obj.save()
        return validated_data

    def validate(self, data):
        email = data['email']
        password = data['password']
        confirm_password = data['confirm_password']
        if password != confirm_password:
            return serializers.ValidationError(f'Passwords different')
        if MyUser.objects.filter(email=email).exists():
            raise serializers.ValidationError(f'This {email} has already registration')
        return data


class MyAuthTokenSerializer(serializers.Serializer):
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
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    email = serializers.EmailField(label="Email", required=True)

    # company = CompanySerializer()

    class Meta:
        model = MyUser
        fields = ('id', 'first_name', 'last_name', 'email', 'password', 'confirm_password')

    # def create(self, validated_data):
    #     first_name = validated_data.pop('first_name')
    #     last_name = validated_data.pop('last_name')
    #     email = validated_data.pop('email')
    #     password = validated_data.pop('password')
    #     company = validated_data.pop('company')
    #     company_name = company.pop('company_name')
    #     company_obj = Company.objects.create(company_name=company_name)
    #     # validated_data['company'] = company
    #     # company_obj.company_name.set(company_name)
    #
    #     user = MyUser.objects.create(first_name=first_name, last_name=last_name, email=email, password=password,
    #                                  company=company_obj, is_staff=True)
    #     user.set_password(password)
    #     user.save()
    #     company_obj.save()
    #     return validated_data

    def validate(self, data):
        email = data['email']
        password = data['password']
        confirm_password = data['confirm_password']
        if password != confirm_password:
            return serializers.ValidationError(f'Passwords different')
        if MyUser.objects.filter(email=email).exists():
            raise serializers.ValidationError(f'This {email} has already registration')
        return data


class CompaniesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ('id', 'company_name', 'address')


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ('id', 'first_name', 'last_name', 'email', 'password')
        read_only_fields = ('id', 'email')
        extra_kwargs = {
            'password': {'write_only': True},
            # 'confirm_password': {'write_only': True},
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


class WorkerOfficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Office
        fields = ('id', 'worker')

    def validate(self, data):
        worker = data['worker']
        if Office.objects.filter(worker=worker).exists():
            raise serializers.ValidationError(f'This {worker} has already working in office')
        return data


class VehicleSerializer(serializers.ModelSerializer):
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
