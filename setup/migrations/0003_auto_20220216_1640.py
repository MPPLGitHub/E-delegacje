# Generated by Django 3.1.7 on 2022-02-16 15:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('setup', '0002_btdelegationrate'),
    ]

    operations = [
        migrations.AddField(
            model_name='btuser',
            name='group',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='auth.group'),
        ),
    ]