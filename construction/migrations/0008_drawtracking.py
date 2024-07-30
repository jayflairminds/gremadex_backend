# Generated by Django 5.0.6 on 2024-07-30 12:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("construction", "0007_budgetmaster"),
    ]

    operations = [
        migrations.CreateModel(
            name="DrawTracking",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("draw_request", models.IntegerField()),
                (
                    "planned_disbursement_amount",
                    models.DecimalField(decimal_places=3, max_digits=30, null=True),
                ),
                (
                    "requested_disbursement_amount",
                    models.DecimalField(decimal_places=3, max_digits=30, null=True),
                ),
                ("date_scheduled", models.DateTimeField(blank=True, null=True)),
                ("date_requested", models.DateTimeField(blank=True, null=True)),
                ("date_approved", models.DateTimeField(blank=True, null=True)),
                ("disbursement_status", models.CharField(max_length=200)),
                (
                    "budget_mastser",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="construction.budgetmaster",
                    ),
                ),
            ],
        ),
    ]