# Generated by Django 4.1.1 on 2022-10-05 13:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0008_remove_cart_session_key_cart_session_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cart',
            old_name='session_id',
            new_name='session',
        ),
    ]