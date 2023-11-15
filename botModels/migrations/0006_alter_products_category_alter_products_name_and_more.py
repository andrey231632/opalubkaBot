# Generated by Django 4.2 on 2023-11-06 10:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("botModels", "0005_products"),
    ]

    operations = [
        migrations.AlterField(
            model_name="products",
            name="category",
            field=models.CharField(max_length=256, verbose_name="Категория"),
        ),
        migrations.AlterField(
            model_name="products",
            name="name",
            field=models.CharField(max_length=256, verbose_name="Название"),
        ),
        migrations.AlterField(
            model_name="products",
            name="price",
            field=models.PositiveBigIntegerField(verbose_name="Цена"),
        ),
        migrations.AlterField(
            model_name="profile",
            name="name",
            field=models.CharField(
                max_length=256, verbose_name="Имя пользователя в тг"
            ),
        ),
        migrations.AlterField(
            model_name="profile",
            name="uniq_name",
            field=models.CharField(
                max_length=256, verbose_name="Уникальное имя пользователя"
            ),
        ),
    ]