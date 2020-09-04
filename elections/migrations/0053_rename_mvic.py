# Generated by Django 3.0.9 on 2020-09-04 09:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0052_ballot_item_name_length'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ballotwebsite',
            old_name='mi_sos_election_id',
            new_name='mvic_election_id',
        ),
        migrations.RenameField(
            model_name='ballotwebsite', old_name='mi_sos_html', new_name='mvic_html',
        ),
        migrations.RenameField(
            model_name='ballotwebsite',
            old_name='mi_sos_precinct_id',
            new_name='mvic_precinct_id',
        ),
        migrations.RenameField(
            model_name='election', old_name='mi_sos_id', new_name='mvic_id',
        ),
        migrations.AlterUniqueTogether(
            name='ballotwebsite',
            unique_together={('mvic_election_id', 'mvic_precinct_id')},
        ),
    ]