# Generated by Django 3.1.7 on 2021-07-30 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('e_delegacje', '0029_btapplicationsettlementmileage_is_agreement_signed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='btapplicationsettlementcost',
            name='attachment',
            field=models.FileField(null=True, upload_to=''),
        ),
    ]
