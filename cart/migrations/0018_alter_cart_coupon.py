# Generated by Django 4.1.2 on 2022-11-05 07:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('coupons', '0016_alter_coupon_max_discount_amount_and_more'),
        ('cart', '0017_cart_coupon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='coupon',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_cart', to='coupons.usercoupon'),
        ),
    ]