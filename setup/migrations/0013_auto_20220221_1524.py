# Generated by Django 3.2.12 on 2022-02-21 14:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('setup', '0012_auto_20220221_1458'),
    ]

    operations = [
        migrations.AlterField(
            model_name='btcostcenter',
            name='text',
            field=models.CharField(max_length=50),
        ),
    ]