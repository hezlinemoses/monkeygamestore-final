# Generated by Django 4.1.2 on 2022-10-27 09:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0016_game_discount_percentage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='discount_percentage',
            field=models.IntegerField(default=0),
        ),
    ]
