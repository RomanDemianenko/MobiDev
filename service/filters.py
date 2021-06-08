import django_filters

from service.models import MyUser, Office, Vehicle


class WorkerFilter(django_filters.FilterSet):
    class Meta:
        model = MyUser
        fields = ['first_name', 'last_name', 'email']


class OfficeFilter(django_filters.FilterSet):
    class Meta:
        model = Office
        fields = ['country', 'city']


class VehicleFilter(django_filters.FilterSet):
    class Meta:
        model = Vehicle
        fields = ['office', 'driver']
