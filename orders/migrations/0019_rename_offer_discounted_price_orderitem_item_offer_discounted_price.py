# Generated by Django 4.1.2 on 2022-10-27 06:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0018_rename_offer_discount_orderitem_offer_discounted_price'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orderitem',
            old_name='offer_discounted_price',
            new_name='item_offer_discounted_price',
        ),
    ]
