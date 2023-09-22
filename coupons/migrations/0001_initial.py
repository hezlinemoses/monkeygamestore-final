# Generated by Django 4.1.2 on 2022-10-31 10:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('discount_type', models.CharField(choices=[('Percentage', 'Percentage'), ('Amount', 'Amount')], max_length=20)),
                ('coupon_type', models.CharField(choices=[('Order', 'Order'), ('Direct to Cart', 'Direct to Cart')], max_length=20)),
                ('discount_percent_value', models.IntegerField(null=True)),
                ('discount_amount_value', models.IntegerField(null=True)),
                ('min_purchase_amount', models.IntegerField(null=True)),
                ('max_discount_amount', models.IntegerField(null=True)),
                ('max_usage_limit', models.IntegerField(null=True)),
                ('max_usage_per_user_limit', models.IntegerField(null=True)),
                ('valid_from', models.DateTimeField(null=True)),
                ('valid_till', models.DateTimeField(null=True)),
                ('order_no', models.IntegerField(null=True, unique=True)),
                ('status', models.CharField(choices=[('Upcoming', 'Upcoming'), ('Ongoing', 'Ongoing'), ('Expired', 'Expired')], max_length=20)),
                ('usage_count', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserCoupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('usage', models.IntegerField(default=0)),
                ('coupon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_coupon', to='coupons.coupon', verbose_name='Coupon')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_coupon', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]