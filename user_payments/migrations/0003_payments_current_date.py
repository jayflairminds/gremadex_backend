# Generated by Django 5.0.6 on 2024-10-15 12:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user_payments", "0002_payments_amount_payments_currency_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="payments",
            name="current_date",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]