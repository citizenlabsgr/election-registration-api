# Generated by Django 2.0.8 on 2018-08-08 03:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('elections', '0017_auto_20180807_2005')]

    operations = [
        migrations.AlterField(
            model_name='election',
            name='mi_sos_id',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='precinct',
            name='mi_sos_id',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]