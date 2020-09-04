# Generated by Django 3.0.9 on 2020-09-04 09:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0053_rename_mvic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ballotwebsite',
            name='mvic_election_id',
            field=models.PositiveIntegerField(verbose_name='MVIC Election ID'),
        ),
        migrations.AlterField(
            model_name='ballotwebsite',
            name='mvic_precinct_id',
            field=models.PositiveIntegerField(verbose_name='MVIC Precinct ID'),
        ),
        migrations.AlterField(
            model_name='candidate',
            name='reference_url',
            field=models.URLField(blank=True, null=True, verbose_name='Reference URL'),
        ),
        migrations.AlterField(
            model_name='election',
            name='mvic_id',
            field=models.PositiveIntegerField(verbose_name='MVIC ID'),
        ),
        migrations.AlterField(
            model_name='election',
            name='reference_url',
            field=models.URLField(blank=True, null=True, verbose_name='Reference URL'),
        ),
        migrations.AlterField(
            model_name='position',
            name='reference_url',
            field=models.URLField(blank=True, null=True, verbose_name='Reference URL'),
        ),
        migrations.AlterField(
            model_name='proposal',
            name='reference_url',
            field=models.URLField(blank=True, null=True, verbose_name='Reference URL'),
        ),
    ]
