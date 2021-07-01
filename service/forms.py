from django import forms
from django.forms import ModelForm

from service.models import MyUser, Company, Office, Vehicle


class LoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = MyUser
        fields = ['email', 'password']


class MyUserForm(ModelForm):
    class Meta:
        model = MyUser
        fields = '__all__'


class RegistCompanyForm(ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    repeat_password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField(required=True)

    def clean_email(self):
        email = self.cleaned_data['email']
        if MyUser.objects.filter(email=email).exists():
            raise forms.ValidationError(f'This {email} has already registration')
        return email

    def clean(self):
        password = self.cleaned_data.get('password')
        repeat_password = self.cleaned_data.get('repeat_password')
        if password != repeat_password:
            raise forms.ValidationError('Inncorect password')
        return self.cleaned_data

    class Meta:
        model = MyUser
        fields = ['first_name', 'last_name', 'email', 'password', 'repeat_password']


class EmployeeProfileForm(ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    repeat_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        password = self.cleaned_data.get('password')
        repeat_password = self.cleaned_data.get('repeat_password')
        if password != repeat_password:
            raise forms.ValidationError('Inncorect password')
        return self.cleaned_data

    class Meta:
        model = MyUser
        fields = ['first_name', 'last_name', 'password', 'repeat_password']


class CompanyCreateForm(ModelForm):
    class Meta:
        model = Company
        fields = ['company_name']


class CompanyForm(ModelForm):
    class Meta:
        model = Company
        fields = '__all__'


class OfficeForm(ModelForm):
    class Meta:
        model = Office
        fields = ['office_name', 'address', 'country', 'city', 'region']


class EmployeeOfficeForm(ModelForm):
    class Meta:
        model = Office
        fields = ['employee']

    def clean_employee(self):
        employee = self.cleaned_data['employee'].id
        if Office.objects.filter(employee=employee).exists():
            raise forms.ValidationError(f'This has already worked in another office')
        return self.cleaned_data

    def clean_same_company(self):
        employee = self.cleaned_data['employee'].company.id
        admin = self.request.user.user.company.id
        if employee != admin:
            raise forms.ValidationError(f'This different company')
        return employee


class VehicleForm(ModelForm):
    class Meta:
        model = Vehicle
        fields = ['licence_plate', 'name', 'model', 'year_of_manufacture']


class VehicleOfficeForm(ModelForm):
    class Meta:
        model = Vehicle
        fields = ['office', 'driver']

    def clean(self):
        driver = self.cleaned_data.get('driver')
        office = self.cleaned_data.get('office')
        if Vehicle.objects.filter(driver=driver).filter(office=office):
            pass
        else:
            raise forms.ValidationError(f'This {driver} work in another office')
        return self.cleaned_data


class VehicleFullForm(ModelForm):
    class Meta:
        model = Vehicle
        fields = '__all__'
