# Generated by Django 3.1.7 on 2021-06-11 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('e_delegacje', '0026_auto_20210609_1730'),
    ]

    operations = [
        migrations.AlterField(
            model_name='btapplication',
            name='approval_date',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
