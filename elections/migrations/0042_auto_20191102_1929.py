# Generated by Django 2.2.6 on 2019-11-02 23:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('elections', '0041_auto_20191102_1518')]

    operations = [
        migrations.AlterField(
            model_name='districtcategory',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='election',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='party', name='description', field=models.TextField(blank=True)
        ),
    ]