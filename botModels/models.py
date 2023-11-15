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
    name = models.CharField(
        max_length=256,
        verbose_name = 'Название',
    )
    description = models.TextField(
        verbose_name = 'Описание',
        max_length = 1024,
    )
    price = models.PositiveBigIntegerField(
        verbose_name = 'Цена',
        null = True,
    )
    image = models.ImageField(
        upload_to='images/'
    )  # Создает поле для загрузки изображений

    def __str__(self):
        return f'#{self.category} {self.name} {self.description} {self.price} {self.image}'


    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        