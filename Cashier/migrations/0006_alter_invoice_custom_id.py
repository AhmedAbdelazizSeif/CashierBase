# Generated by Django 5.0 on 2024-01-02 10:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Cashier", "0005_invoice_custom_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="invoice",
            name="custom_id",
            field=models.CharField(editable=False, max_length=20, unique=True),
        ),
    ]
