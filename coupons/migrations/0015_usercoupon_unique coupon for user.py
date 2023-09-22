# Generated by Django 4.1.2 on 2022-11-04 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coupons', '0014_alter_usercoupon_unique_together'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='usercoupon',
            constraint=models.UniqueConstraint(fields=('coupon', 'user'), name='unique coupon for user'),
        ),
    ]