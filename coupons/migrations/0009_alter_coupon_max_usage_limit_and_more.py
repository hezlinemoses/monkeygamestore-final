# Generated by Django 4.1.2 on 2022-11-04 05:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coupons', '0008_alter_coupon_discount_percent_value_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='max_usage_limit',
            field=models.PositiveIntegerField(null=True, verbose_name='Usage Limit'),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='max_usage_per_user_limit',
            field=models.PositiveIntegerField(null=True, verbose_name='Usage Limit Per User'),
        ),
    ]
