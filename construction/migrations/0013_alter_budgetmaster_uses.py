# Generated by Django 5.0.6 on 2024-08-05 05:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("construction", "0012_budgetmaster_uses_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="budgetmaster",
            name="uses",
            field=models.CharField(max_length=150),
        ),
    ]
