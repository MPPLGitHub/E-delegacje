# Generated by Django 3.2.12 on 2022-02-20 17:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('setup', '0007_auto_20220220_1821'),
    ]

    operations = [
        migrations.CreateModel(
            name='BtCompanyCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('compamy_code', models.CharField(max_length=4)),
                ('company_name', models.CharField(max_length=80)),
            ],
        ),
        migrations.AddField(
            model_name='btuser',
            name='vendor_id',
            field=models.CharField(default='11', max_length=10),
        ),
        migrations.AddField(
            model_name='btuser',
            name='company_code',
            field=models.ManyToManyField(default=1, to='setup.BtCompanyCode'),
        ),
    ]