# Generated by Django 4.1.1 on 2022-09-17 16:46

import accounts.managers
from django.conf import settings
import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyUser',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='User id')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists'}, help_text='Between 5-20 characters. Alphabets, numbers and @ . + - _ characters.', max_length=20, unique=True, validators=[django.contrib.auth.validators.ASCIIUsernameValidator(), django.core.validators.MinLengthValidator(5), django.core.validators.ProhibitNullCharactersValidator], verbose_name='Username')),
                ('email', models.EmailField(error_messages={'unique': 'A user with this email already exists'}, max_length=254, unique=True, verbose_name='Email')),
                ('first_name', models.CharField(blank=True, help_text='Only Alphabets', max_length=50, null=True, validators=[django.core.validators.RegexValidator(code='Invalid name', message='Only alphabets and space', regex='^[a-zA-Z ]+$')], verbose_name='First Name')),
                ('last_name', models.CharField(blank=True, help_text='Only Alphabets!!', max_length=50, null=True, validators=[django.core.validators.RegexValidator(code='Invalid name', message='Only alphabets and space', regex='^[a-zA-Z ]+$')], verbose_name='Last Name')),
                ('phone', models.BigIntegerField(error_messages={'unique': 'A user with this phone number already exists'}, unique=True, validators=[django.core.validators.MinLengthValidator(10), django.core.validators.MaxLengthValidator(10), django.core.validators.ProhibitNullCharactersValidator])),
                ('is_customer', models.BooleanField(default=False)),
                ('is_verified', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('is_superuser', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('objects', accounts.managers.MyUserManager()),
            ],
        ),
        migrations.CreateModel(
            name='address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, help_text='Only Alphabets', max_length=50, null=True, validators=[django.core.validators.RegexValidator(code='Invalid name', message='Only alphabets and space', regex='^[a-zA-Z ]+$')], verbose_name='First Name')),
                ('last_name', models.CharField(blank=True, help_text='Only Alphabets!!', max_length=50, null=True, validators=[django.core.validators.RegexValidator(code='Invalid name', message='Only alphabets and space', regex='^[a-zA-Z ]+$')], verbose_name='Last Name')),
                ('line_1', models.CharField(max_length=150, verbose_name='Line 1')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User Id')),
            ],
        ),
    ]