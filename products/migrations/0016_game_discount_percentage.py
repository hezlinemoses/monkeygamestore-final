# Generated by Django 4.1.2 on 2022-10-27 06:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0015_game_discount_end_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='discount_percentage',
            field=models.IntegerField(null=True),
        ),
    ]
