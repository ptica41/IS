from django.db import models

from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils import timezone

from phonenumber_field.modelfields import PhoneNumberField


class UserManager(BaseUserManager):
    def create_user(self, username, name, surname, phone, email, password=None, commit=True, **kwargs):
        if not username:
            raise ValueError('User must have a username')
        if not name:
            raise ValueError('User must have a first name')
        if not surname:
            raise ValueError('User must have a surname')
        if not phone:
            raise ValueError('User must have a phone')
        if not email:
            raise ValueError('User must have a email')

        user = self.model(username=username, name=name, surname=surname, phone=phone, email=email, **kwargs)

        user.set_password(password)

        if commit:
            user.save(using=self._db)

        return user

    def create_superuser(self, username, name, surname, phone, email, password):
        user = self.create_user(username, name, surname, phone, email, password, commit=False)
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    objects = UserManager()

    id = models.AutoField(primary_key=True)
    username = models.CharField(verbose_name='Логин', max_length=50, unique=True)
    name = models.CharField(verbose_name='Имя', max_length=50)
    surname = models.CharField(verbose_name='Фамилия', max_length=50)
    middle_name = models.CharField(verbose_name='Отчество', max_length=50, blank=True, null=True)
    phone = PhoneNumberField(verbose_name='Телефон')
    email = models.EmailField(verbose_name='email')
    date_joined = models.DateTimeField(verbose_name='Дата создания', default=timezone.now)
    last_login = models.DateTimeField(verbose_name='Онлайн', blank=True, null=True)
    is_superuser = models.BooleanField(verbose_name='Админ?', default=False)
    is_active = models.BooleanField(verbose_name='Активный пользователь?', default=True)

    USERNAME_FIELD = 'username'

    class Meta:
        db_table = 'Users'
        verbose_name_plural = 'Пользователи'
        ordering = ['-id']

    def __str__(self):
        return f'{self.surname} {self.name}'


class Group(models.Model):
    objects = models.Manager()

    id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name='Название группы', unique=True)
    is_active = models.BooleanField(verbose_name='Актив / архив', default=True)

    class Meta:
        db_table = 'Groups'
        verbose_name_plural = 'Группы'
        ordering = ['-id']

    def __str__(self):
        return self.name


class UserGroup(models.Model):
    objects = models.Manager()

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    group = models.ForeignKey(Group, verbose_name='Группа', on_delete=models.CASCADE)

    class Meta:
        db_table = 'UsersGroups'
        verbose_name_plural = 'Пользователи-Группы'
        ordering = ['-id']

    def __str__(self):
        return f'{self.group} | {self.user}'


class Organization(models.Model):
    objects = models.Manager()

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, verbose_name='Название', unique=True)
    address = models.CharField(verbose_name='Адрес', blank=True, null=True)
    group = models.ForeignKey(Group, verbose_name='Группа', on_delete=models.CASCADE)

    class Meta:
        db_table = 'Organizations'
        verbose_name_plural = 'Организации'
        ordering = ['-id']

    def __str__(self):
        return self.name


class Object(models.Model):
    objects = models.Manager()

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, verbose_name='Название')
    contact = models.CharField(verbose_name='Контактное лицо', blank=True, null=True)
    group = models.ForeignKey(Group, verbose_name='Группа', on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, verbose_name='Организация', on_delete=models.CASCADE)

    class Meta:
        db_table = 'Objects'
        verbose_name_plural = 'Объекты информатизации'
        ordering = ['-id']

    def __str__(self):
        return self.name


class Infosystem(models.Model):
    objects = models.Manager()

    CHOICES = [
        ('GIS', 'ГИС'),
        ('ISPDN', 'ИСПДн'),
        ('GIS_ISPDN', 'ГИС + ИСПДн')
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, verbose_name='Название')
    address = models.CharField(verbose_name='Адрес', blank=True, null=True)
    type = models.CharField(verbose_name='Тип', choices=CHOICES)
    clss = models.CharField(max_length=50, verbose_name='Класс защищенности', blank=True, null=True)
    clss_info = models.CharField(verbose_name='Информация о классе защищенности', blank=True, null=True)
    level = models.CharField(max_length=50, verbose_name='Уровень защищенности', blank=True, null=True)
    level_info = models.CharField(verbose_name='Информация о уровне защищенности', blank=True, null=True)
    contact = models.CharField(verbose_name='Контактное лицо', blank=True, null=True)
    obj = models.ForeignKey(Object, verbose_name='Объект информатизации', on_delete=models.CASCADE)

    class Meta:
        db_table = 'Infosystems'
        verbose_name_plural = 'Информационные системы'
        ordering = ['-id']

    def __str__(self):
        return self.name


class Place(models.Model):
    objects = models.Manager()

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, verbose_name='Название')
    address = models.CharField(verbose_name='Адрес', blank=True, null=True)
    is_active = models.BooleanField(verbose_name='Актив / архив', default=True)
    infosystem = models.ForeignKey(Infosystem, verbose_name='Информационная система', on_delete=models.CASCADE)

    class Meta:
        db_table = 'Places'
        verbose_name_plural = 'Места'
        ordering = ['-id']

    def __str__(self):
        return self.name


class Project(models.Model):
    objects = models.Manager()

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, verbose_name='Название')
    deadline = models.DateField(verbose_name='Срок завершения')
    is_check = models.BooleanField(verbose_name='Проверен / нет', default=False)
    is_finished = models.BooleanField(verbose_name='Действующий / завершен', default=False)
    infosystem = models.ForeignKey(Infosystem, verbose_name='Информационная система', on_delete=models.CASCADE)
    group_rp = models.ForeignKey(Group, verbose_name='Руководители', on_delete=models.CASCADE)
    group_work = models.ForeignKey(Group, verbose_name='Исполнители', on_delete=models.CASCADE)

    class Meta:
        db_table = 'Projects'
        verbose_name_plural = 'Проекты'
        ordering = ['-id']

    def __str__(self):
        return self.name


class Checklist(models.Model):
    objects = models.Manager()

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, verbose_name='Название')
    is_check = models.BooleanField(verbose_name='Проверен /нет', default=False)
    project = models.ForeignKey(Project, verbose_name='Проект', on_delete=models.CASCADE)

    class Meta:
        db_table = 'Checklists'
        verbose_name_plural = 'Чек-листы'
        ordering = ['-id']

    def __str__(self):
        return self.name
