# Generated by Django 4.1.2 on 2022-11-03 20:35

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('offerss', '0013_alter_categoryoffer_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categoryoffer',
            name='discount_percentage',
            field=models.PositiveIntegerField(null=True, validators=[django.core.validators.MaxValueValidator(60)]),
        ),
        migrations.AlterField(
            model_name='mainsaleoffer',
            name='discount_percentage',
            field=models.PositiveIntegerField(null=True, validators=[django.core.validators.MaxValueValidator(60)]),
        ),
        migrations.AlterField(
            model_name='productoffer',
            name='discount_percentage',
            field=models.PositiveIntegerField(null=True, validators=[django.core.validators.MaxValueValidator(60)]),
        ),
    ]