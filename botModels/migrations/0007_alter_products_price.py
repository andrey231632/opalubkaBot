# Generated by Django 4.2 on 2023-11-06 15:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("botModels", "0006_alter_products_category_alter_products_name_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="products",
            name="price",
            field=models.PositiveBigIntegerField(
                default=None, null=True, verbose_name="Цена"
            ),
        ),
    ]