# Generated by Django 4.2.7 on 2023-12-05 01:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0007_remove_hives_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='hives',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
