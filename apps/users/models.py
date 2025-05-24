from django.contrib.auth.models import AbstractUser, PermissionsMixin, BaseUserManager
from django.db import models

class UserType(models.Model):
    title = models.CharField(
        max_length=155,
        verbose_name='Тип пользователя',
        help_text="Введите какого типа пользователя хотите добавить!"
    )

    def __str__(self):
        return self.title


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, role=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        if not role:
            raise ValueError('Role is required')
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        role, _ = UserType.objects.get_or_create(title='admin')
        return self.create_user(email, password, role=role, is_staff=True, is_superuser=True, **extra_fields)


class User(AbstractUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    role = models.ForeignKey(UserType, on_delete=models.PROTECT, related_name='users')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    phone = models.CharField(max_length=155, verbose_name='Номер телефона')
    # только для исполнителей
    is_verified = models.BooleanField(default=False)
    replies_balance = models.PositiveIntegerField(default=0)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    class Meta:
        verbose_name_plural = 'Пользователи'