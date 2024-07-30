# Generated by Django 5.0.6 on 2024-07-30 12:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("construction", "0006_constructionstatus_contingencystatus_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="BudgetMaster",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("project_total", models.IntegerField()),
                ("loan_budget", models.IntegerField()),
                ("acquisition_loan", models.IntegerField()),
                ("building_loan", models.IntegerField()),
                ("project_loan", models.IntegerField()),
                ("mezzanine_loan", models.IntegerField()),
                ("current_reviesed_budget", models.IntegerField()),
                ("total_funded", models.IntegerField()),
                ("remaining_to_fund", models.IntegerField()),
                ("total_funded_percentage", models.IntegerField()),
                ("uses", models.CharField(max_length=50)),
                (
                    "loan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="construction.loan",
                    ),
                ),
            ],
        ),
    ]
