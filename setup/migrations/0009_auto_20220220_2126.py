# Generated by Django 3.2.12 on 2022-02-20 20:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('setup', '0008_auto_20220220_1847'),
    ]

    operations = [
        migrations.RenameField(
            model_name='btcompanycode',
            old_name='compamy_code',
            new_name='company_code',
        ),
    ]
