# Generated by Django 4.2.7 on 2023-12-04 12:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_hives_active_hivesplaces_active_mothers_active_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hives',
            name='place',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.hivesplaces'),
        ),
        migrations.AlterField(
            model_name='mothers',
            name='hive',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='myapp.hives'),
        ),
    ]