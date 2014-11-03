from django.contrib.auth.models import UserManager as BaseUserManager
from django.db import models


class UserQuerySet(models.QuerySet):
    pass


class UserManager(BaseUserManager):
    def create_user(self, phone, password, **fields):
        if not phone:
            raise ValueError('Users must have a phone number')

        if 'email' in fields:
            fields['email'] = self.normalize_email(fields['email'])

        user = self.model(phone=phone, **fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password, **fields):
        user = self.create_user(phone, password, **fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(update_fields=['is_staff', 'is_superuser'], using=self._db)
        return user


UserManager = UserManager.from_queryset(UserQuerySet)
PassengerManager = UserManager
DriverManager = UserManager
