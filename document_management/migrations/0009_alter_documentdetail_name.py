# Generated by Django 5.0.6 on 2024-09-09 04:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("document_management", "0008_alter_documentdetail_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="documentdetail",
            name="name",
            field=models.CharField(max_length=800, null=True),
        ),
    ]
