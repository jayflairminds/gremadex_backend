# Generated by Django 5.0.6 on 2024-10-24 08:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("document_management", "0014_merge_0013_document_summary_0013_drawdocuments"),
    ]

    operations = [
        migrations.AlterField(
            model_name="feedback",
            name="comment",
            field=models.CharField(max_length=265),
        ),
    ]
