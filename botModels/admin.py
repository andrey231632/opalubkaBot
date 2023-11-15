from django.contrib import admin
from .models import Profile, Products
from .forms import ProfileForm, ProductForm
from django.utils.safestring import mark_safe


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('chat_id', 'name', 'uniq_name', 'phone_number')
    form = ProfileForm


@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin): 
    list_display = ('category', 'name', 'description',  'price', 'display_image')
    form = ProductForm 

    def display_image(self, obj):
        return mark_safe(f'<img src={obj.image.url} width = "50" height = "60">')
    
    display_image.short_description = 'Изображение'
    