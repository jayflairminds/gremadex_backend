# Generated by Django 5.0.6 on 2024-07-11 13:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project_details', '0002_rename_borrower_id_loan_borrower_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='loandisbursementschedule',
            old_name='loan_id',
            new_name='loan',
        ),
    ]
