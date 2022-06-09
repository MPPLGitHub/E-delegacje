# Generated by Django 3.2.12 on 2022-03-21 14:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('setup', '0013_auto_20220221_1524'),
    ]

    operations = [
        migrations.CreateModel(
            name='BtOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.CharField(max_length=12, null=True, unique=True)),
                ('name', models.CharField(max_length=50)),
                ('cost_center', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bt_orders', to='setup.btcostcenter')),
            ],
        ),
        migrations.DeleteModel(
            name='BtUserVendor',
        ),
    ]