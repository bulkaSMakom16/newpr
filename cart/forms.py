from django import forms
from .models import Product, Order

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock']

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = []

class PaymentForm(forms.Form):
    first_name = forms.CharField(label='Имя', max_length=100)
    last_name = forms.CharField(label='Фамилия', max_length=100)
    address = forms.CharField(label='Адрес', max_length=255)
    city = forms.CharField(label='Город', max_length=100)
    department = forms.CharField(label='Отделение', max_length=100)
