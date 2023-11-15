from django import forms

from .models import Profile, Products


class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = (
            'chat_id',
            'name',
            'uniq_name',
            'phone_number',
        )
        widgets = {
            'name': forms.TextInput,
            'uniq_name': forms.TextInput,  
            'phone_number': forms.TextInput,  
        }
    

class ProductForm(forms.ModelForm):

    class Meta:
        model = Products
        fields = (
            'category',
            'name',
            'description',
            'price',
            'image',
        )
        widgets = {
            'category': forms.TextInput,
            'name': forms.TextInput,
            'description': forms.Textarea,  
            'price': forms.NumberInput,  
            # 'image': forms.ImageField,
        }

