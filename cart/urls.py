from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),  
    path('update/<int:product_id>/', views.update_cart, name='update_cart'),
    path('add_product/', views.add_product, name='add_product'),
    path('products/', views.product_list, name='product_list'),
]