from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import check_password
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.views.generic import CreateView, TemplateView, ListView, UpdateView, RedirectView, DeleteView, DetailView
from django_filters.views import FilterView

from service.filters import WorkerFilter, OfficeFilter
from service.forms import LoginForm, RegistCompanyForm, CompanyForm, WorkerProfileForm, OfficeForm, WorkerOfficeForm, \
    VehicleForm, VehicleFullForm, VehicleOfficeForm, CompanyCreateForm
from service.models import MyUser, Company, Office, Vehicle


class CompanyRegistrationView(CreateView):
    """User can create profile and company, and user get admin role in this company"""
    model = MyUser

    def get(self, request, *args, **kwargs):
        form = RegistCompanyForm(request.POST)
        formA = CompanyCreateForm(request.POST)
        # films = Seance.objects.all()
        context = {'form': form, 'formA': formA}
        return render(request, 'company_regist.html', context)

    def post(self, request, *args, **kwargs):
        form = RegistCompanyForm(request.POST)
        formA = CompanyCreateForm(request.POST)
        if form.is_valid() and formA.is_valid():
            new_user = form.save(commit=False)
            new_company = formA.save(commit=False)
            new_company.company_name = formA.cleaned_data['company_name']
            new_user.username = form.cleaned_data['first_name']
            new_user.name = form.cleaned_data['last_name']
            new_company.save()
            new_user.email = form.cleaned_data['email']
            new_user.company = new_company
            new_user.save()
            new_user.set_password(form.cleaned_data['password'])
            new_user.is_superuser = True
            new_user.save()
            # user = authenticate(email=form.cleaned_data['email'], password=form.cleaned_data['password'])
            login(request, new_user, backend='service.email_authenticate.UserEmailBackend')
            messages.success(request, 'Welcome in our club')
            return HttpResponseRedirect('/service/')

        context = {'form': form, 'formA': formA}
        return render(request, 'company_regist.html', context)


class UserLogout(LogoutView):
    template_name = 'logout.html'
    next_page = '/service/'


class ServiceList(ListView):
    model = Company
    ordering = ['-id']
    paginate_by = 10
    template_name = 'service.html'
    context_object_name = 'obj'


class WorkerCreate(PermissionRequiredMixin, CreateView):
    """Admin can create a worker"""
    permission_required = 'request.user.is_superuser'
    model = MyUser

    def get(self, request, *args, **kwargs):
        form = RegistCompanyForm(request.POST)
        context = {'form': form}
        return render(request, 'worker_create.html', context)

    def post(self, request, *args, **kwargs):
        form = RegistCompanyForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.username = form.cleaned_data['first_name']
            new_user.name = form.cleaned_data['last_name']
            new_user.email = form.cleaned_data['email']
            new_user.company = request.user.company
            new_user.save()
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            messages.success(request, 'Welcome in our club')
            return HttpResponseRedirect('/service/')

        context = {'form': form}
        return render(request, 'worker_create.html', context)


class WorkerList(PermissionRequiredMixin, ListView, FilterView):
    """Admin can see list of workers and filter them by first name, last name, email"""
    permission_required = 'request.user.is_superuser'
    model = Company, MyUser
    ordering = ['-id']
    paginate_by = 10
    template_name = 'worker_list.html'
    filterset_class = WorkerFilter

    def get_queryset(self):
        queryset = MyUser.objects.filter(company=self.request.user.company, is_superuser=False)
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class WorkersFilter(PermissionRequiredMixin, FilterView):
    permission_required = 'request.user.is_superuser'
    model = Company, MyUser
    template_name = 'worker_list.html'
    filterset_class = WorkerFilter


class WorkerDetail(DetailView):
    '''Admin can see details of worker profile'''
    permission_required = 'request.user.is_superuser'
    model = MyUser
    form_class = MyUser
    template_name = 'profile.html'
    context_object_name = 'worker'


class WorkerUpdate(PermissionRequiredMixin, UpdateView):
    '''Admin can change worker`s detail '''
    permission_required = 'request.user.is_superuser'
    model = MyUser
    form_class = WorkerProfileForm
    template_name = 'worker_update.html'
    success_url = '/service/'

    def post(self, request, *args, **kwargs):
        worker_pk = self.kwargs['pk']
        worker = MyUser.objects.get(id=worker_pk)
        form = WorkerProfileForm(request.POST, instance=worker)
        if form.is_valid():
            worker = form.save(commit=False)
            worker.username = form.cleaned_data['first_name']
            worker.name = form.cleaned_data['last_name']
            worker.save()
            worker.set_password(form.cleaned_data['password'])
            worker.save()
            messages.success(self.request, "You Change details")
            return HttpResponseRedirect('/service/')
        else:
            messages.warning(self.request, 'Passwords don`t the same')
        context = {'form': form}
        return render(request, 'worker_update.html', context)


class WorkerDelete(PermissionRequiredMixin, DeleteView):
    '''Superuser can delete workers'''
    permission_required = 'request.user.is_superuser'
    model = MyUser
    template_name = 'worker_delete.html'
    success_url = '/service/'
    context_object_name = 'obj'


class CompanyDetail(DetailView):
    """Admin and worker can see details of them company"""
    permission_required = 'request.user.is_authenticated'
    model = Company
    form_class = CompanyForm
    template_name = 'company_detail.html'
    context_object_name = 'company'


class CompanyUpdate(PermissionRequiredMixin, UpdateView):
    """Admin can change details of company"""
    permission_required = 'request.user.is_superuser'
    model = Company
    form_class = CompanyForm
    template_name = 'company_update.html'
    success_url = '/service/'


class ProfileUpdate(UpdateView):
    '''Admin ar worker can change Profile detail by themself '''
    model = MyUser
    form_class = WorkerProfileForm
    template_name = 'worker_update.html'
    success_url = '/service/'

    def post(self, request, *args, **kwargs):
        worker_pk = self.kwargs['pk']
        worker = MyUser.objects.get(id=worker_pk)
        form = WorkerProfileForm(request.POST, instance=worker)
        if form.is_valid():
            worker = form.save(commit=False)
            worker.username = form.cleaned_data['first_name']
            worker.name = form.cleaned_data['last_name']
            worker.save()
            worker.set_password(form.cleaned_data['password'])
            worker.save()
            messages.success(self.request, "You Change details")
            return HttpResponseRedirect('/service/')
        else:
            messages.warning(self.request, 'Passwords don`t the same')
        context = {'form': form}
        return render(request, 'worker_update.html', context)


class OfficeCreate(PermissionRequiredMixin, CreateView):
    '''Admin can create a office of his company'''
    permission_required = 'request.user.is_superuser'
    model = Office
    form_class = OfficeForm
    success_url = '/service/'
    template_name = 'office_create.html'

    def get(self, request, *args, **kwargs):
        form = OfficeForm(request.POST)
        context = {'form': form}
        return render(request, 'office_create.html', context)

    def post(self, request, *args, **kwargs):
        form = OfficeForm(request.POST)
        if form.is_valid():
            new_office = form.save(commit=False)
            new_office.office_name = form.cleaned_data['office_name']
            new_office.address = form.cleaned_data['address']
            new_office.country = form.cleaned_data['country']
            new_office.city = form.cleaned_data['city']
            new_office.region = form.cleaned_data['region']
            new_office.company = request.user.company
            new_office.save()
            messages.success(request, 'You create a new office')
            return HttpResponseRedirect('/service/')

        context = {'form': form}
        return render(request, 'office_create.html', context)


class OfficeList(ListView, FilterView):
    """Worker and admin can see list of offices of them company"""
    model = Office
    form = OfficeForm
    ordering = ['-id']
    paginate_by = 10
    template_name = 'office_list.html'
    filterset_class = OfficeFilter

    def get_queryset(self):
        queryset = Office.objects.filter(company=self.request.user.company)
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class OfficeDetail(PermissionRequiredMixin, DetailView):
    '''Superuser can see details the office'''
    permission_required = 'request.user.is_superuser'
    model = Office
    form_class = OfficeForm
    template_name = 'office_detail.html'


class OfficeUpdate(PermissionRequiredMixin, UpdateView):
    '''Superuser can change details of office'''
    permission_required = 'request.user.is_superuser'
    model = Office
    form_class = OfficeForm
    template_name = 'office_update.html'
    success_url = '/service/'


class OfficeDelete(PermissionRequiredMixin, DeleteView):
    '''Superuser can delete the office'''
    permission_required = 'request.user.is_superuser'
    model = Office
    template_name = 'office_delete.html'
    success_url = '/service/'
    context_object_name = 'obj'


class AddWorkerToOfficeUpdate(PermissionRequiredMixin, UpdateView):
    """Admin can appoint a worker to office"""
    permission_required = 'request.user.is_superuser'
    model = Office
    form_class = WorkerOfficeForm
    success_url = '/service/'
    template_name = 'add_worker_to_office.html'

    def get(self, request, *args, **kwargs):
        form = WorkerOfficeForm(request.POST)
        workers = MyUser.objects.filter(company=self.request.user.company)
        context = {'form': form, "workers": workers}
        return render(request, 'add_worker_to_office.html', context)

    def post(self, request, *args, **kwargs):
        office_pk = self.kwargs['pk']
        office = Office.objects.get(id=office_pk)
        form = WorkerOfficeForm(request.POST, instance=office)
        if form.is_valid():
            add_worker = form.save(commit=False)
            add_worker.company = request.user.company
            add_worker.worker = form.cleaned_data['worker']

            # add_worker.company = request.user.company
            add_worker.save()
            messages.success(request, 'You add a worker to office')
            return HttpResponseRedirect('/service/')

        context = {'form': form}
        return render(request, 'add_worker_to_office.html', context)


class WorkerOfficeList(ListView):
    """Worker can see  details of his office, if he appoint to office"""
    model = Company, MyUser, Office
    ordering = ['-id']
    paginate_by = 10
    template_name = 'office_detail_worker.html'
    context_object_name = 'obj'

    def get_queryset(self):
        queryset = Office.objects.filter(worker=self.request.user)
        return queryset


class VehicleCreate(PermissionRequiredMixin, CreateView):
    """Admin can create vehicles"""
    permission_required = 'request.user.is_superuser'
    model = Vehicle
    form_class = VehicleForm
    template_name = 'vehicle_create.html'
    success_url = '/service/'

    def get(self, request, *args, **kwargs):
        form = VehicleForm(request.POST)
        context = {'form': form}
        return render(request, 'vehicle_create.html', context)

    def post(self, request, *args, **kwargs):
        form = VehicleForm(request.POST)
        if form.is_valid():
            new_vehicle = form.save(commit=False)
            new_vehicle.company = request.user.company
            new_vehicle.save()
            messages.success(request, 'You create a new office')
            return HttpResponseRedirect('/service/')

        context = {'form': form}
        return render(request, 'vehicle_create.html', context)


class VehicleList(PermissionRequiredMixin, ListView, FilterView):
    """Admin can see vehicle list of his company"""
    permission_required = 'request.user.is_superuser'
    model = Vehicle
    form_class = VehicleFullForm
    ordering = ['-id']
    paginate_by = 10
    template_name = 'vehicle_list.html'
    filterset_class = OfficeFilter

    def get_queryset(self):
        queryset = Vehicle.objects.filter(company=self.request.user.company)
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class AddWorkerToVehicleUpdate(PermissionRequiredMixin, UpdateView):
    """Admin can appoint vehicle to worker"""
    permission_required = 'request.user.is_superuser'
    model = Office
    form_class = VehicleOfficeForm
    success_url = '/service/'
    template_name = 'add_worker_to_office.html'

    def get(self, request, *args, **kwargs):
        form = VehicleOfficeForm(request.POST)
        context = {'form': form}
        return render(request, 'add_worker_to_office.html', context)

    def post(self, request, *args, **kwargs):
        vehicle_pk = self.kwargs['pk']
        vehicle = Vehicle.objects.get(id=vehicle_pk)
        form = VehicleOfficeForm(request.POST, instance=vehicle)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.company = request.user.company
            # vehicle.office = form.cleaned_data['office']
            # vehicle.driver = form.cleaned_data['driver']
            vehicle.save()
            messages.success(request, 'You add a worker to office')
            return HttpResponseRedirect('/service/')

        context = {'form': form}
        return render(request, 'add_worker_to_office.html', context)


class VehicleUpdate(PermissionRequiredMixin, UpdateView):
    """Admin can update vehicle of his company"""
    permission_required = 'request.user.is_superuser'
    model = Vehicle
    form_class = VehicleForm
    template_name = 'vehicle_update.html'
    success_url = '/service/'


class VehicleDelete(PermissionRequiredMixin, DeleteView):
    """Admin can delete vehicle of his company"""
    permission_required = 'request.user.is_superuser'
    model = Vehicle
    template_name = 'vehicle_delete.html'
    success_url = '/service/'
    context_object_name = 'obj'


class MyVehicleList(ListView):
    """User can see list of vehicle which he can drive"""
    model = Vehicle
    form_class = VehicleForm
    ordering = ['-id']
    paginate_by = 10
    template_name = 'yourself_vehicle.html'
    context_object_name = 'obj'

    def get_queryset(self):
        queryset = Vehicle.objects.filter(driver=self.request.user)
        return queryset
