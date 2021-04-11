# Generated by Django 3.1.7 on 2021-04-11 13:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('e_delegacje', '0001_initial'),
        ('setup', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='btapplicationsettlementmileage',
            name='bt_milage_rate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bt_application_settlement_mileages', to='setup.btmileagerates'),
        ),
        migrations.AddField(
            model_name='btapplicationsettlementinfo',
            name='advance_payment',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='bt_application_settlement_info', to='e_delegacje.btapplication'),
        ),
        migrations.AddField(
            model_name='btapplicationsettlementinfo',
            name='bt_application_settlement',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='bt_application', to='e_delegacje.btapplicationsettlement'),
        ),
        migrations.AddField(
            model_name='btapplicationsettlementfeeding',
            name='bt_application_settlement',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bt_application_settlement_feeding', to='e_delegacje.btapplicationsettlement'),
        ),
        migrations.AddField(
            model_name='btapplicationsettlementcost',
            name='bt_application_settlement',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bt_application_settlement_costs', to='e_delegacje.btapplicationsettlement'),
        ),
        migrations.AddField(
            model_name='btapplicationsettlementcost',
            name='bt_cost_currency',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bt_application_settlement_costs', to='setup.btratestax'),
        ),
        migrations.AddField(
            model_name='btapplicationsettlement',
            name='bt_application_id',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='bt_applications_settlements', to='e_delegacje.btapplication'),
        ),
        migrations.AddField(
            model_name='btapplication',
            name='CostCenter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bt_applications', to='setup.btcostcenter'),
        ),
        migrations.AddField(
            model_name='btapplication',
            name='application_author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bt_applications_author', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='btapplication',
            name='target_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bt_applications', to=settings.AUTH_USER_MODEL),
        ),
    ]
