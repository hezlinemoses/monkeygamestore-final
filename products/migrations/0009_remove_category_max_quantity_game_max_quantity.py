# Generated by Django 4.1.1 on 2022-10-14 06:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_category_is_discountable_category_max_quantity'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='max_quantity',
        ),
        migrations.AddField(
            model_name='game',
            name='max_quantity',
            field=models.IntegerField(default=10),
        ),
    ]
