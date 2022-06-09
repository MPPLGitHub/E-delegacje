# Generated by Django 3.2.12 on 2022-02-21 12:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('setup', '0010_auto_20220221_1319'),
    ]

    operations = [
        migrations.AddField(
            model_name='btuserauthorisation',
            name='company_code',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='bt_user_authorisations', to='setup.btcompanycode'),
            preserve_default=False,
        ),
    ]