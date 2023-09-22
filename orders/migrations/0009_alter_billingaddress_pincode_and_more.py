# Generated by Django 4.1.1 on 2022-10-07 10:52

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0008_alter_billingaddress_user_alter_order_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billingaddress',
            name='pincode',
            field=models.CharField(max_length=6, validators=[django.core.validators.ProhibitNullCharactersValidator, django.core.validators.RegexValidator(code='invalid_pin_code', message='Enter a valid pincode', regex='^[0-9]+$')], verbose_name='PINCODE'),
        ),
        migrations.AlterField(
            model_name='shippingaddress',
            name='pincode',
            field=models.CharField(max_length=6, validators=[django.core.validators.ProhibitNullCharactersValidator, django.core.validators.RegexValidator(code='invalid_pin_code', message='Enter a valid pincode', regex='^[0-9]+$')], verbose_name='PINCODE'),
        ),
    ]
