# Generated by Django 4.1.1 on 2022-10-08 18:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0011_alter_cartitem_game'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='total',
        ),
    ]
