# Generated by Django 4.2 on 2023-11-06 10:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("botModels", "0004_rename_external_id_profile_chat_id_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Products",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("category", models.PositiveBigIntegerField(verbose_name="Категория")),
                ("name", models.TextField(verbose_name="Название")),
                ("description", models.TextField(verbose_name="Описание")),
                ("price", models.TextField(verbose_name="Цена")),
                ("image", models.ImageField(upload_to="images/")),
            ],
            options={
                "verbose_name": "Товар",
                "verbose_name_plural": "Товары",
            },
        ),
    ]
