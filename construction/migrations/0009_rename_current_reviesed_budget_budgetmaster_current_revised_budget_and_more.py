# Generated by Django 5.0.6 on 2024-07-31 05:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("construction", "0008_drawtracking"),
    ]

    operations = [
        migrations.RenameField(
            model_name="budgetmaster",
            old_name="current_reviesed_budget",
            new_name="current_revised_budget",
        ),
        migrations.RenameField(
            model_name="drawtracking",
            old_name="budget_mastser",
            new_name="budget_master",
        ),
        migrations.AddField(
            model_name="budgetmaster",
            name="project_type",
            field=models.CharField(max_length=50, null=True),
        ),
    ]