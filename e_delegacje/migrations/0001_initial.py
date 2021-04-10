# Generated by Django 3.1.7 on 2021-04-10 07:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BtApplication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trip_category', models.CharField(choices=[('kr', 'krajowa'), ('zg', 'zagraniczna')], max_length=2)),
                ('application_status', models.CharField(choices=[('saved', 'Zapisany'), ('in_progress', 'W akceptacji'), ('approved', 'Zaakcdptowany'), ('settled', 'Rozliczony'), ('canceled', 'Anulowany')], max_length=30)),
                ('employee_level', models.CharField(choices=[('lvl1', 'podstawowy'), ('lvl2', 'kierownik'), ('lvl3', 'dyrektor'), ('lvl4', 'dyrektor regionu'), ('lvl5', 'dyrektor dywizji'), ('lvl6', 'członek zarządu'), ('lvl7', 'prezes zarządu')], max_length=30)),
                ('application_date', models.DateField(auto_now_add=True)),
                ('trip_purpose_text', models.CharField(max_length=250)),
                ('transport_type', models.CharField(choices=[('train', 'pociąg'), ('plane', 'samolot'), ('company_car', 'samochód służbowy'), ('own_car', 'własny samochód'), ('other', 'inny')], max_length=30)),
                ('travel_route', models.CharField(max_length=120)),
                ('planned_start_date', models.DateField()),
                ('planned_end_date', models.DateField()),
                ('advance_payment', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='BtApplicationSettlement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bt_application_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bt_applications_settlements', to='e_delegacje.btapplication')),
            ],
        ),
        migrations.CreateModel(
            name='BtCostCenter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='BtDepartment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('cost_center', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='Bt_Departments', to='e_delegacje.btcostcenter')),
                ('manager_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='Bt_Departments', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BtDivision',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('manager', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='BtLocation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('profit_center', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='BtMileageRates',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vehicle_type', models.CharField(choices=[('car_under_900cm3', 'auto o pojemności do 900cm3'), ('car_above_900cm3', 'auto o pojemności powyżej 900cm3'), ('motorbike', 'motocykl'), ('moped', 'motorowe')], max_length=20)),
                ('rate', models.DecimalField(decimal_places=4, max_digits=6)),
            ],
        ),
        migrations.CreateModel(
            name='BtRatesTax',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('diet_rates', models.IntegerField()),
                ('etc', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='BtRegion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='BtSubmissionStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submission_text', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='BtUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employee_level', models.CharField(max_length=100)),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bt_Users', to='e_delegacje.btdepartment')),
                ('division', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bt_Users', to='e_delegacje.btdivision')),
                ('manager', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bt_Users', to='e_delegacje.btlocation')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='btdepartment',
            name='profit_center',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='Bt_Departments', to='e_delegacje.btlocation'),
        ),
        migrations.AddField(
            model_name='btcostcenter',
            name='profit_center_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='Bt_CostCenters', to='e_delegacje.btlocation'),
        ),
        migrations.CreateModel(
            name='BtApplicationSettlementMileage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bt_car_reg_number', models.CharField(max_length=8)),
                ('trip_start_place', models.CharField(max_length=50)),
                ('trip_date', models.DateField()),
                ('trip_description', models.CharField(max_length=120)),
                ('trip_purpose', models.CharField(max_length=240)),
                ('mileage', models.DecimalField(decimal_places=2, max_digits=8)),
                ('bt_application_settlement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bt_application_settlement_mileages', to='e_delegacje.btapplicationsettlement')),
                ('bt_milage_rate', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bt_application_settlement_mileages', to='e_delegacje.btmileagerates')),
            ],
        ),
        migrations.CreateModel(
            name='BtApplicationSettlementInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bt_completed', models.BooleanField()),
                ('bt_start_date', models.DateField()),
                ('bt_start_time', models.TimeField()),
                ('bt_end_date', models.DateField()),
                ('bt_end_time', models.TimeField()),
                ('advance_payment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='bt_application_settlement_info', to='e_delegacje.btapplicationsettlement')),
                ('bt_application_settlement', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='bt_application', to='e_delegacje.btapplicationsettlement')),
            ],
        ),
        migrations.CreateModel(
            name='BtApplicationSettlementFeeding',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('breakfast_quantity', models.IntegerField()),
                ('dinner_quantity', models.IntegerField()),
                ('supper_quantity', models.IntegerField()),
                ('bt_application_settlement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bt_application_settlement_feeding', to='e_delegacje.btapplicationsettlement')),
            ],
        ),
        migrations.CreateModel(
            name='BtApplicationSettlementCost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bt_cost_category', models.CharField(choices=[('accommodation', 'nocleg'), ('transport', 'dojazd'), ('luggage', 'bagaż'), ('other', 'inne')], max_length=40)),
                ('bt_cost_amount', models.DecimalField(decimal_places=2, max_digits=8)),
                ('bt_cost_document_date', models.DateField()),
                ('bt_cost_VAT_rate', models.CharField(choices=[('W1', '23 %'), ('W7', '7 %'), ('WN', 'nie dotyczy'), ('W0', 'zwolniony')], max_length=10)),
                ('bt_application_settlement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bt_application_settlement_costs', to='e_delegacje.btapplicationsettlement')),
                ('bt_cost_currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bt_application_settlement_costs', to='e_delegacje.btratestax')),
            ],
        ),
        migrations.AddField(
            model_name='btapplication',
            name='CostCenter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bt_applications', to='e_delegacje.btcostcenter'),
        ),
        migrations.AddField(
            model_name='btapplication',
            name='application_author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bt_applications_author', to='e_delegacje.btuser'),
        ),
        migrations.AddField(
            model_name='btapplication',
            name='target_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bt_applications', to='e_delegacje.btuser'),
        ),
    ]
