# Generated by Django 5.0 on 2024-01-02 07:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("profile_app", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="otp",
            field=models.CharField(blank=True, max_length=6),
        ),
        migrations.AddField(
            model_name="customuser",
            name="otp_created_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
