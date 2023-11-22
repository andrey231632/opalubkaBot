from django.db import models

class Profile(models.Model):
    chat_id = models.PositiveBigIntegerField(
        verbose_name = 'ID пользователя в тг',
        unique = True,
    )
    name = models.CharField(
        max_length=256,
        verbose_name = 'Имя пользователя в тг',
    )
    uniq_name = models.CharField(
        max_length=256,
        verbose_name = 'Уникальное имя пользователя',
    )
    phone_number = models.TextField(
        verbose_name = 'Номер телефона',
    )
    language_code = models.CharField(
        max_length=4,
        verbose_name = 'Язык',
        default = 'ru',
    )

    def __str__(self):
        return f'#{self.chat_id} {self.name} {self.uniq_name} {self.phone_number}'


    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'


class Products(models.Model):
    category = models.CharField(
        max_length=256,
        verbose_name = 'Категория',
    )
    name_ru = models.CharField(
        max_length=256,
        verbose_name = 'Название на русском',
        default = 'Имя',
    )
    name_uz = models.CharField(
        max_length=256,
        verbose_name = 'Название на узбекском',
        default = 'Имя',
    )
    description_ru = models.TextField(
        verbose_name = 'Описание на русском',
        max_length = 1024,
        default = 'Описание',
    )
    description_uz = models.TextField(
        verbose_name = 'Описание на узбекском',
        max_length = 1024,
        default = 'Описание',
    )
    price = models.PositiveBigIntegerField(
        verbose_name = 'Цена',
        null = True,
    )
    image = models.ImageField(
        upload_to='images/'
    )  # Создает поле для загрузки изображений

    def __str__(self):
        return f'#{self.category} {self.name_ru} {self.name_uz} {self.description_ru} {self.description_uz} {self.price} {self.image}'


    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        