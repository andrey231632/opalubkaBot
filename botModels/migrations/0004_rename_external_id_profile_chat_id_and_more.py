# Generated by Django 4.2 on 2023-10-30 13:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("botModels", "0003_profile_phone_number_alter_profile_external_id_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="profile",
            old_name="external_id",
            new_name="chat_id",
        ),
        migrations.AlterField(
            model_name="profile",
            name="phone_number",
            field=models.TextField(verbose_name="Номер телефона"),
        ),
    ]