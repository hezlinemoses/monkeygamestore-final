# Generated by Django 4.1.2 on 2022-10-27 06:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0020_rename_item_discount_percentage_orderitem_item_offer_discount_percentage'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orderitem',
            old_name='item_offer_discounted_price',
            new_name='item_offer_discount_given',
        ),
    ]
