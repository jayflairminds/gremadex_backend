# Generated by Django 5.0.6 on 2024-08-09 06:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("document_management", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="document",
            name="file_id",
            field=models.CharField(max_length=255, null=True),
        ),
    ]
