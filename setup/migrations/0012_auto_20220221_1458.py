# Generated by Django 3.2.12 on 2022-02-21 13:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('setup', '0011_auto_20220221_1334'),
    ]

    operations = [
        migrations.AddField(
            model_name='btcostcenter',
            name='company_code',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='Bt_CostCenters', to='setup.btcompanycode'),
            preserve_default=False,
        ),
    ]
