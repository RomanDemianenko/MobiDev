from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model
from service.models import MyUser


class UserEmailBackend(ModelBackend):
    '''
    Класс-обработчик для аутентификации пользователей по
    email-адресу.
    '''
    def authenticate(self, request, username="", password="", **kwargs):
        '''
        Переопределяем метод аутентификации.
        '''
        user_model = get_user_model()
        try:
            # Ищем совпадение по email у пользовательских моделей в БД.
            # Если находим - сверяем пароли.
            user = user_model.objects.get(email__iexact=username)
            if check_password(password, user.password):
                return user
            else:
                return None
        # В случае "неуспеха" проверки ловим соответствующее
        # исключение и возвращаем отрицательный результат.
        except user_model.DoesNotExist:
            return None